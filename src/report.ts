import { colors } from "es-toolkit/server"

import { installableId, installableKey } from "./installables/installables"
import type {
    InstallStep,
    PackageChannel,
    PlanNode,
    SystemPlanNode,
} from "./installs/plan"
import type { ConfigResult, ConfigTarget, ConfigType } from "./types/configs"
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

const CONFIG_TYPE_LABELS: Record<ConfigType, string> = {
    "file-copy": "",
    "json-merge": " (merge)",
}

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
 * @param target Config file of the plan
 * @description Returns the line of the config file in the plan.
 */
const planLineOfConfig = (target: ConfigTarget): string =>
    target.skip
        ? colors.gray(`      ◦ ${target.destination} (already current)`)
        : `      ◦ ${target.destination}${CONFIG_TYPE_LABELS[target.type]}`

/**
 * @param installable Kind and identifier of the installable
 * @param targets Config files of the plan
 * @description Returns the config files that the installable holds.
 */
const configsOf = (installable: Installable, targets: ConfigTarget[]): ConfigTarget[] =>
    targets.filter(
        target => installableKey(target.installable) === installableKey(installable),
    )

/**
 * @param nodes Nodes of the plan
 * @param targets Config files of the plan
 * @description Returns the lines of the plan, with one group per kind and the configs under their node.
 */
const kindLines = (nodes: PlanNode[], targets: ConfigTarget[]): string[] =>
    KIND_ORDER.flatMap(kind => {
        const ofKind = nodes.filter(node => node.installable[0] === kind)
        return ofKind.length === 0
            ? []
            : [colors.bold(`  ${KIND_LABELS[kind]}`)].concat(
                  ofKind.flatMap(node =>
                      [planLineOfNode(node)].concat(
                          configsOf(node.installable, targets).map(planLineOfConfig),
                      ),
                  ),
              )
    })

/**
 * @param nodes Nodes of the plan
 * @param targets Config files of the plan
 * @description Returns the lines of the config files that no node of the plan holds.
 * @remarks Covers the applications that the operating system provides, because no node installs them.
 */
const looseConfigLines = (nodes: PlanNode[], targets: ConfigTarget[]): string[] => {
    const covered = new Set(nodes.map(node => installableKey(node.installable)))
    const loose = targets.filter(
        target => !covered.has(installableKey(target.installable)),
    )

    return loose.length === 0
        ? []
        : [colors.bold("  configs")].concat(
              [
                  ...new Set(loose.map(target => installableId(target.installable))),
              ].flatMap(id =>
                  [`    • ${id}`].concat(
                      loose
                          .filter(target => installableId(target.installable) === id)
                          .map(planLineOfConfig),
                  ),
              ),
          )
}

/**
 * @param steps Steps of the plan, in install order
 * @param targets Config files of the plan, `null` when the run skips them
 * @description Reports every installable and every config file of the plan.
 */
export const reportPlan = (
    steps: InstallStep[],
    targets: ConfigTarget[] | null,
): void => {
    const nodes = steps.flatMap(nodesOfStep)
    const pendingNodes = nodes.filter(node => !node.skip)
    const configs = targets ?? []
    const pendingConfigs = configs.filter(target => !target.skip)

    console.log(colors.bold("Plan"))
    console.log(
        [
            colors.bold(
                `  installables: ${pendingNodes.length} to install, ${
                    nodes.length - pendingNodes.length
                } already present`,
            ),
            targets === null
                ? colors.gray("  configs: skipped")
                : colors.bold(
                      `  configs: ${pendingConfigs.length} to copy, ${
                          configs.length - pendingConfigs.length
                      } already current`,
                  ),
            "",
            ...kindLines(nodes, configs),
            ...looseConfigLines(nodes, configs),
        ].join("\n"),
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
 * @param result Outcome of one config file
 * @description Reports a config file that reached its destination.
 */
export const reportConfigApplied = (result: ConfigResult): void => {
    const destination = result.target.destination
    if (result.status === "unchanged") {
        console.log(colors.gray(`  = ${destination} (already current)`))
        return
    }

    console.log(colors.green(`  ✓ ${destination}`))
    if (result.backupPath !== null) {
        console.log(colors.gray(`    backup: ${result.backupPath}`))
    }
}

/**
 * @param target Config file of the plan
 * @param message Text of the error
 * @description Reports a config file that did not reach its destination.
 */
export const reportConfigFailure = (target: ConfigTarget, message: string): void => {
    console.log(colors.red(`  ✗ ${target.destination}: ${message}`))
}

/**
 * @param targets Config files that the plan leaves out
 * @description Reports the config files of the applications that did not install.
 */
export const reportConfigSkipped = (targets: ConfigTarget[]): void => {
    console.log(
        colors.yellow(
            `  ⊘ ${targets
                .map(target => target.destination)
                .join(", ")}: the application did not install`,
        ),
    )
}

/** @description Reports the start of the config copy. */
export const reportConfigsStart = (): void => {
    console.log("")
    console.log(colors.cyan(colors.bold("Configs")))
}

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @description Reports the command that the process runs next.
 */
export const reportCommand = (command: string, args: string[]): void => {
    console.log(colors.dim(`  $ ${[command, ...args].join(" ")}`))
}
