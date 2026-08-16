import { colors } from "es-toolkit/server"

import { installableId } from "./installables/installables"
import type {
    InstallStep,
    PackageChannel,
    PlanNode,
    SystemPlanNode,
} from "./installs/plan"
import type { Installable, InstallableKind } from "./types/installables"
import type { Platform } from "./types/platforms"

const PLATFORM_LABELS: Record<Platform, string> = {
    "arch-linux": "Arch Linux",
    "mac-os": "macOS",
    windows: "Windows",
}

const CHANNEL_LABELS: Record<PackageChannel, string> = {
    "arch-standard": "pacman",
    "arch-aur": "paru",
    "brew-formula": "brew",
    "brew-cask": "brew --cask",
}

const KIND_LABELS: Record<InstallableKind, string> = {
    application: "applications",
    library: "libraries",
    toolchain: "toolchains",
    extension: "extensions",
}

const KIND_ORDER: InstallableKind[] = ["application", "library", "toolchain", "extension"]

/**
 * @param step Step of the plan
 * @description Returns the nodes that the step covers.
 */
export const nodesOfStep = (step: InstallStep): PlanNode[] =>
    step.type === "custom" ? [step.node] : step.nodes

/**
 * @param step Step of the plan
 * @description Returns the name of the channel of the step, or of its custom install.
 */
export const stepLabel = (step: InstallStep): string =>
    step.type === "custom"
        ? `custom install of ${installableId(step.node.installable)}`
        : CHANNEL_LABELS[step.channel]

/**
 * @param index Position of the step in the plan
 * @param total Number of steps of the plan
 * @param step Step of the plan
 * @description Returns the header line of the step.
 */
const stepHeader = (index: number, total: number, step: InstallStep): string =>
    colors.cyan(colors.bold(`Step ${index + 1}/${total} — ${stepLabel(step)}`))

/**
 * @param installables Installables to name
 * @description Returns the identifiers of the installables as one list.
 */
const idList = (installables: Installable[]): string =>
    installables.map(installableId).join(", ")

/**
 * @param platform Target operating system
 * @description Reports the platform of this machine.
 */
export const reportPlatform = (platform: Platform): void => {
    console.log(colors.bold(`Platform: ${PLATFORM_LABELS[platform]}`))
    console.log("")
}

/**
 * @param nodes Nodes of the applications that the operating system provides
 * @description Reports the presence of every base system application.
 */
export const reportBaseSystem = (nodes: SystemPlanNode[]): void => {
    console.log(colors.bold("Base system"))
    console.log(
        nodes
            .map(node => {
                const id = installableId(node.installable)
                return node.skip ? colors.green(`  ✓ ${id}`) : colors.red(`  ✗ ${id}`)
            })
            .join("\n"),
    )
    console.log("")
}

/**
 * @param missing Nodes of the base system applications that are absent
 * @description Reports the base system applications that this machine does not provide.
 */
export const reportBaseSystemFailure = (missing: SystemPlanNode[]): void => {
    console.error(
        colors.red(
            `The base system does not provide: ${idList(
                missing.map(node => node.installable),
            )}`,
        ),
    )
    console.error(colors.red("Install these applications, then run this command again."))
}

/**
 * @param node Node of the plan
 * @description Returns the line of the node in the plan.
 */
const planLineOfNode = (node: PlanNode): string => {
    const id = installableId(node.installable)
    return node.skip ? colors.gray(`    • ${id} (already installed)`) : `    • ${id}`
}

/**
 * @param steps Steps of the plan, in install order
 * @description Reports every installable of the plan, with one group per kind.
 */
export const reportPlan = (steps: InstallStep[]): void => {
    const nodes = steps.flatMap(nodesOfStep)
    const pending = nodes.filter(node => !node.skip)

    console.log(
        colors.bold(
            `Plan: ${pending.length} to install, ${
                nodes.length - pending.length
            } already present`,
        ),
    )
    console.log(
        KIND_ORDER.flatMap(kind => {
            const ofKind = nodes.filter(node => node.installable[0] === kind)
            return ofKind.length === 0
                ? []
                : [colors.bold(`  ${KIND_LABELS[kind]}`)].concat(
                      ofKind.map(planLineOfNode),
                  )
        }).join("\n"),
    )
    console.log("")
}

/**
 * @param step Step of the plan
 * @param index Position of the step in the plan
 * @param total Number of steps of the plan
 * @description Reports the start of a step.
 */
export const reportStepStart = (
    step: InstallStep,
    index: number,
    total: number,
): void => {
    console.log(stepHeader(index, total, step))
}

/** @description Reports a run that has no install to make. */
export const reportNothingToInstall = (): void => {
    console.log(colors.gray("Nothing to install."))
}

/**
 * @param blockers Dependencies that did not install
 * @param installables Installables that the blockers hold back
 * @description Reports the installables that a failed dependency blocks.
 */
export const reportBlocked = (
    blockers: Installable[],
    installables: Installable[],
): void => {
    console.log(
        colors.yellow(
            `  ⊘ ${idList(installables)}: the dependencies failed (${idList(blockers)})`,
        ),
    )
}

/**
 * @param installables Installables that the command covers
 * @description Reports an install command that ended with code 0.
 */
export const reportInstalled = (installables: Installable[]): void => {
    console.log(colors.green(`  ✓ ${idList(installables)}`))
}

/**
 * @param installables Installables that the command covers
 * @param message Text of the error
 * @description Reports an install command that failed.
 */
export const reportInstallFailure = (
    installables: Installable[],
    message: string,
): void => {
    console.log(colors.red(`  ✗ ${idList(installables)}: ${message}`))
}

/** @description Reports that the dry run is complete. */
export const reportDryRun = (): void => {
    console.log(colors.gray("Dry run: no install ran."))
}

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @description Reports the command that the process runs next.
 */
export const reportCommand = (command: string, args: string[]): void => {
    console.log(colors.dim(`  $ ${[command, ...args].join(" ")}`))
}
