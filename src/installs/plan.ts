import { uniqBy } from "es-toolkit"
import { pipe } from "es-toolkit/fp"
import { match, P } from "ts-pattern"

import {
    applications,
    extensions,
    libraries,
    toolchains,
    userApplications,
} from "../data"
import type {
    DependencyCycle,
    InstallableUnavailable,
    InstallError,
    PlanError,
    UnsupportedInstall,
} from "../errors"
import { formatInstallable, installableKey } from "../installables/installables"
import { Result } from "../shared/result"
import type { SystemApplication } from "../types/applications/applications"
import type { InstallableEntity, InstancedEntity } from "../types/entities"
import type { Installable, InstallableKey } from "../types/installables"
import type {
    CustomInstallType,
    PackageInstall,
    PackageInstallType,
} from "../types/installs"
import type { Platform } from "../types/platforms"
import {
    installArchLinuxPackagesFromAurParu,
    installArchLinuxPackagesFromStandardRepos,
    installHomebrewCaskPackages,
    installHomebrewFormulaePackages,
} from "./installs"
import {
    isAurArchLinuxPackageInstalled,
    isBrewCaskPackageInstalled,
    isBrewFormulaePackageInstalled,
    isStandardArchLinuxPackageInstalled,
} from "./verification"

export type PackageChannel = "arch-standard" | "arch-aur" | "brew-formula" | "brew-cask"

const PACKAGE_CHANNELS: PackageChannel[] = [
    "arch-standard",
    "arch-aur",
    "brew-formula",
    "brew-cask",
]

interface PlanNodeBase {
    installable: Installable
    requires: Installable[]
    skip: boolean
}

export interface PackagePlanNode extends PlanNodeBase {
    type: PackageInstallType
    channel: PackageChannel
    packageName: string
}

export interface CustomPlanNode extends PlanNodeBase {
    type: CustomInstallType
    install: () => Promise<Result<void, InstallError>>
}

export interface SystemPlanNode extends PlanNodeBase {
    type: "system"
}

export type PlanNode = PackagePlanNode | CustomPlanNode | SystemPlanNode

export interface PackageInstallStep {
    type: PackageInstallType
    channel: PackageChannel
    nodes: PackagePlanNode[]
    install: (packageNames: string[]) => () => Promise<Result<void, InstallError>>
}

export interface CustomInstallStep {
    type: CustomInstallType
    node: CustomPlanNode
}

export type InstallStep = PackageInstallStep | CustomInstallStep

export interface InstallPlan {
    systemApplications: SystemPlanNode[]
    steps: InstallStep[]
}

/**
 * @param installable Kind and identifier of the installable
 * @param install Package install of the instance
 * @description Returns the channel that installs the package.
 */
const channelOf = (
    installable: Installable,
    install: PackageInstall,
): Result<PackageChannel, UnsupportedInstall> =>
    match(install)
        .returnType<Result<PackageChannel, UnsupportedInstall>>()
        .with({ manager: "pacman" }, () => Result.ok("arch-standard"))
        .with({ manager: "paru" }, () => Result.ok("arch-aur"))
        .with({ manager: "brew", cask: false }, () => Result.ok("brew-formula"))
        .with({ manager: "brew", cask: true }, () => Result.ok("brew-cask"))
        .with({ manager: "winget" }, () =>
            Result.err({
                type: "unsupported-install",
                installable,
                message: `The winget install of the ${formatInstallable(
                    installable,
                )} is not supported yet`,
            }),
        )
        .exhaustive()

/**
 * @param channel Channel that installs the package
 * @param packageName Name of the package
 * @description Returns the command that verifies the package of the channel.
 */
const checkerOf = (channel: PackageChannel, packageName: string) =>
    match(channel)
        .with("arch-standard", () => isStandardArchLinuxPackageInstalled(packageName))
        .with("arch-aur", () => isAurArchLinuxPackageInstalled(packageName))
        .with("brew-formula", () => isBrewFormulaePackageInstalled(packageName))
        .with("brew-cask", () => isBrewCaskPackageInstalled(packageName))
        .exhaustive()

/**
 * @param channel Channel that installs the package
 * @description Returns the command that installs the packages of the channel.
 */
const installerOf = (channel: PackageChannel) =>
    match(channel)
        .with("arch-standard", () => installArchLinuxPackagesFromStandardRepos)
        .with("arch-aur", () => installArchLinuxPackagesFromAurParu)
        .with("brew-formula", () => installHomebrewFormulaePackages)
        .with("brew-cask", () => installHomebrewCaskPackages)
        .exhaustive()

/**
 * @param installable Kind and identifier of the installable
 * @param platform Target operating system
 * @description Builds the error of an installable that the platform does not cover.
 */
const unavailable = (
    installable: Installable,
    platform: Platform,
): InstallableUnavailable => ({
    type: "installable-unavailable",
    installable,
    platform,
    message: `The ${formatInstallable(installable)} has no install for ${platform}`,
})

/**
 * @param installable Kind and identifier of the installable
 * @param application Application that the operating system provides
 * @param platform Target operating system
 * @description Builds the node of a system application, and reads its presence.
 * @remarks A missing system application stays in the plan, because no install can add it.
 */
const resolveSystemNode = async (
    installable: Installable,
    application: SystemApplication,
    platform: Platform,
): Promise<Result<PlanNode, PlanError>> => {
    if (application.platform !== platform) {
        return Result.err(unavailable(installable, platform))
    }

    const installed = await application.instance.isInstalled()
    if (!installed.success) {
        return installed
    }

    return Result.ok<PlanNode>({
        type: "system",
        installable,
        requires: [],
        skip: installed.value,
    })
}

/**
 * @param installable Kind and identifier of the installable
 * @param entity Entity that holds one instance per platform
 * @param platform Target operating system
 * @description Builds the node of the platform instance, and reads its presence.
 */
const resolveInstancedNode = (
    installable: Installable,
    entity: InstancedEntity,
    platform: Platform,
): Promise<Result<PlanNode, PlanError>> => {
    const instance = entity.instances[platform]
    if (instance === null) {
        return Promise.resolve(Result.err(unavailable(installable, platform)))
    }

    return match(instance)
        .returnType<Promise<Result<PlanNode, PlanError>>>()
        .with({ install: { type: "custom" } }, async ({ install, isInstalled }) => {
            const installed = await isInstalled()
            if (!installed.success) {
                return installed
            }

            return Result.ok<PlanNode>({
                type: "custom",
                installable,
                requires: install.requires,
                install: install.install,
                skip: installed.value,
            })
        })
        .with({ install: { type: "package" } }, async ({ install }) => {
            const channel = channelOf(installable, install)
            if (!channel.success) {
                return channel
            }

            const installed = await checkerOf(channel.value, install.packageName)()
            if (!installed.success) {
                return installed
            }

            return Result.ok<PlanNode>({
                type: "package",
                installable,
                requires: install.requires,
                channel: channel.value,
                packageName: install.packageName,
                skip: installed.value,
            })
        })
        .exhaustive()
}

/**
 * @param installable Kind and identifier of the installable
 * @description Returns the entity that the installable points to.
 */
const entityOf = (installable: Installable): InstallableEntity =>
    match(installable)
        .returnType<InstallableEntity>()
        .with(["application", P.select()], id => applications[id])
        .with(["library", P.select()], id => libraries[id])
        .with(["toolchain", P.select()], id => toolchains[id])
        .with(["extension", P.select()], id => extensions[id])
        .exhaustive()

/**
 * @param installable Kind and identifier of the installable
 * @param platform Target operating system
 * @description Builds the node of any installable, whatever its kind.
 */
const resolveNode = (
    installable: Installable,
    platform: Platform,
): Promise<Result<PlanNode, PlanError>> => {
    const entity = entityOf(installable)
    if (!("instances" in entity)) {
        return resolveSystemNode(installable, entity, platform)
    }

    return resolveInstancedNode(installable, entity, platform)
}

/**
 * @param installables Installables to resolve
 * @param platform Target operating system
 * @param collected Nodes of the previous rounds
 * @description Builds the node of every installable, then of every dependency.
 * @remarks Resolves one dependency level per round, and each round runs its checks in parallel.
 */
const collectNodes = async (
    installables: Installable[],
    platform: Platform,
    collected: Map<InstallableKey, PlanNode>,
): Promise<Result<Map<InstallableKey, PlanNode>, PlanError>> => {
    const pending = uniqBy(installables, installableKey).filter(
        installable => !collected.has(installableKey(installable)),
    )
    if (pending.length === 0) {
        return Result.ok(collected)
    }

    const resolved = Result.sequence(
        await Promise.all(pending.map(installable => resolveNode(installable, platform))),
    )
    if (!resolved.success) {
        return resolved
    }

    const entries: Array<[InstallableKey, PlanNode]> = resolved.value.map(node => [
        installableKey(node.installable),
        node,
    ])

    return collectNodes(
        resolved.value.flatMap(node => node.requires),
        platform,
        new Map([...collected, ...entries]),
    )
}

/**
 * @param node Node to place
 * @param nodes Every node of the plan
 * @param visiting Installables of the current branch
 * @description Returns the depth of the node in the dependency tree.
 * @remarks A node of level N installs after every node of level N-1.
 */
const levelOf = (
    node: PlanNode,
    nodes: Map<InstallableKey, PlanNode>,
    visiting: Installable[],
): Result<number, DependencyCycle> => {
    const key = installableKey(node.installable)
    const path = [...visiting, node.installable]
    if (visiting.some(installable => installableKey(installable) === key)) {
        return Result.err<DependencyCycle>({
            type: "dependency-cycle",
            path,
            message: `The dependencies form a cycle: ${path
                .map(formatInstallable)
                .join(" -> ")}`,
        })
    }

    const dependencies = node.requires.flatMap(installable => {
        const dependency = nodes.get(installableKey(installable))
        return dependency === undefined ? [] : [dependency]
    })

    return pipe(
        Result.sequence(dependencies.map(dependency => levelOf(dependency, nodes, path))),
        Result.map(levels => (levels.length === 0 ? 0 : 1 + Math.max(...levels))),
    )
}

/**
 * @param nodes Nodes of one level
 * @description Builds the steps of one level, with one step per package channel.
 * @remarks Groups the packages of a channel into one step, so the package manager runs once.
 */
const stepsOfLevel = (nodes: PlanNode[]): InstallStep[] => {
    const packageNodes = nodes.filter(node => node.type === "package")

    return [
        ...nodes
            .filter(node => node.type === "custom")
            .map((node): CustomInstallStep => ({ type: "custom", node })),
        ...PACKAGE_CHANNELS.map(channel => ({
            channel,
            nodes: packageNodes.filter(node => node.channel === channel),
        }))
            .filter(group => group.nodes.length > 0)
            .map((group): PackageInstallStep => ({
                type: "package",
                channel: group.channel,
                nodes: group.nodes,
                install: installerOf(group.channel),
            })),
    ]
}

/**
 * @param platform Target operating system
 * @description Returns every installable that the platform covers, of every kind.
 */
const rootsOf = (platform: Platform): Installable[] => [
    ...Object.values(userApplications)
        .filter(application => application.instances[platform] !== null)
        .map((application): Installable => ["application", application.id]),
    ...Object.values(libraries)
        .filter(entity => entity.instances[platform] !== null)
        .map((entity): Installable => ["library", entity.id]),
    ...Object.values(toolchains)
        .filter(entity => entity.instances[platform] !== null)
        .map((entity): Installable => ["toolchain", entity.id]),
    ...Object.values(extensions)
        .filter(entity => entity.instances[platform] !== null)
        .map((entity): Installable => ["extension", entity.id]),
]

/**
 * @param platform Target operating system
 * @description Builds the base system state and the ordered install steps of the platform.
 * @remarks The order depends on the platform alone, so an installed node stays in the plan with `skip` set.
 */
export const buildInstallPlan = async (
    platform: Platform,
): Promise<Result<InstallPlan, PlanError>> => {
    const collected = await collectNodes(rootsOf(platform), platform, new Map())
    if (!collected.success) {
        return collected
    }

    const nodes = [...collected.value.values()]
    const leveled = Result.sequence(
        nodes.map(node =>
            pipe(
                levelOf(node, collected.value, []),
                Result.map(level => ({ node, level })),
            ),
        ),
    )
    if (!leveled.success) {
        return leveled
    }

    const levels = [...new Set(leveled.value.map(entry => entry.level))].toSorted(
        (first, second) => first - second,
    )

    return Result.ok({
        systemApplications: nodes
            .filter(node => node.type === "system")
            .toSorted((first, second) =>
                installableKey(first.installable).localeCompare(
                    installableKey(second.installable),
                ),
            ),
        steps: levels.flatMap(level =>
            stepsOfLevel(
                leveled.value
                    .filter(entry => entry.level === level)
                    .map(entry => entry.node),
            ),
        ),
    })
}
