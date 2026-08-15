import process, { argv } from "node:process"

import { colors } from "es-toolkit/server"

import { parseCliOptions } from "./cli"
import type { InstallError } from "./errors"
import { installableId, installableKey } from "./installables/installables"
import { buildInstallPlan } from "./installs/plan"
import type { InstallStep, PackageChannel, SystemPlanNode } from "./installs/plan"
import { platform } from "./shared/platform"
import type { Result } from "./shared/result"
import type { Installable, InstallableKey } from "./types/installables"

type OutcomeStatus = "installed" | "planned" | "already-installed" | "failed" | "blocked"

interface Outcome {
    installable: Installable
    status: OutcomeStatus
    detail: string
}

interface TargetNode {
    installable: Installable
    requires: Installable[]
    skip: boolean
}

const CHANNEL_LABELS: Record<PackageChannel, string> = {
    "arch-standard": "pacman",
    "arch-aur": "paru",
    "brew-formula": "brew",
    "brew-cask": "brew --cask",
}

/**
 * @param node Node to install
 * @param failed Keys of the installables that did not install
 * @description Returns the dependencies of the node that did not install.
 */
const blockersOf = (node: TargetNode, failed: Set<InstallableKey>): Installable[] =>
    node.requires.filter(installable => failed.has(installableKey(installable)))

/**
 * @param node Node that the plan skips
 * @description Reports a node that is present already, and returns its outcome.
 */
const toAlreadyInstalled = (node: TargetNode): Outcome => {
    console.log(
        colors.gray(`• ${installableId(node.installable)}: skipping, already installed`),
    )
    return {
        installable: node.installable,
        status: "already-installed",
        detail: "",
    }
}

/**
 * @param node Node that the plan skips
 * @param blockers Dependencies that did not install
 * @description Reports a node that its dependencies block, and returns its outcome.
 */
const toBlocked = (node: TargetNode, blockers: Installable[]): Outcome => {
    const detail = `The dependencies failed: ${blockers.map(installableId).join(", ")}`
    console.log(
        colors.yellow(`• ${installableId(node.installable)}: skipping, ${detail}`),
    )
    return {
        installable: node.installable,
        status: "blocked",
        detail,
    }
}

/**
 * @param label Name of the install on the terminal
 * @param install Command that installs the nodes
 * @param nodes Nodes that the command covers
 * @param dryRun True when the command must not run
 * @description Runs one install command, and returns the outcome of every node it covers.
 */
const runInstall = async (
    label: string,
    install: () => Promise<Result<void, InstallError>>,
    nodes: TargetNode[],
    dryRun: boolean,
): Promise<Outcome[]> => {
    console.log(colors.cyan(`→ ${label}`))

    if (dryRun) {
        return nodes.map((node): Outcome => ({
            installable: node.installable,
            status: "planned",
            detail: "",
        }))
    }

    const result = await install()

    if (!result.success) {
        console.log(colors.red(`✗ ${label}`))
        return nodes.map((node): Outcome => ({
            installable: node.installable,
            status: "failed",
            detail: result.error.message,
        }))
    }

    console.log(colors.green(`✓ ${label}`))
    return nodes.map((node): Outcome => ({
        installable: node.installable,
        status: "installed",
        detail: "",
    }))
}

/**
 * @param step Step of the plan
 * @param failed Keys of the installables that did not install
 * @param dryRun True when no install must run
 * @description Runs one step of the plan, and returns the outcome of every node.
 * @remarks Skips the nodes that are present already, and the nodes that a failed dependency blocks.
 */
const runStep = async (
    step: InstallStep,
    failed: Set<InstallableKey>,
    dryRun: boolean,
): Promise<Outcome[]> => {
    if (step.type === "custom") {
        if (step.node.skip) {
            return [toAlreadyInstalled(step.node)]
        }

        const blockers = blockersOf(step.node, failed)
        return blockers.length > 0
            ? [toBlocked(step.node, blockers)]
            : runInstall(
                  installableId(step.node.installable),
                  step.node.install,
                  [step.node],
                  dryRun,
              )
    }

    const skipped = step.nodes.filter(node => node.skip).map(toAlreadyInstalled)
    const pending = step.nodes.filter(node => !node.skip)
    const blocked = pending
        .map(node => ({ node, blockers: blockersOf(node, failed) }))
        .filter(entry => entry.blockers.length > 0)
        .map(entry => toBlocked(entry.node, entry.blockers))

    const runnable = pending.filter(node => blockersOf(node, failed).length === 0)
    if (runnable.length === 0) {
        return [...skipped, ...blocked]
    }

    const label = `${runnable
        .map(node => installableId(node.installable))
        .join(", ")} (${CHANNEL_LABELS[step.channel]})`

    return [
        ...skipped,
        ...blocked,
        ...(await runInstall(
            label,
            step.install(runnable.map(node => node.packageName)),
            runnable,
            dryRun,
        )),
    ]
}

/**
 * @param nodes Nodes of the applications that the operating system provides
 * @description Reports the state of the base system, and returns one outcome per node.
 */
const reportSystemApplications = (nodes: SystemPlanNode[]): Outcome[] => {
    console.log(colors.bold("Base system"))

    const outcomes = nodes.map((node): Outcome => {
        const id = installableId(node.installable)
        console.log(node.skip ? colors.green(`  ✓ ${id}`) : colors.red(`  ✗ ${id}`))
        return {
            installable: node.installable,
            status: node.skip ? "already-installed" : "failed",
            detail: node.skip ? "" : "The base system does not provide it",
        }
    })

    console.log("")
    return outcomes
}

/**
 * @param outcomes Outcome of every node of the plan
 * @param dryRun True when no install ran
 * @description Reports the totals of the run, and sets the exit code on a failure.
 */
const reportOutcomes = (outcomes: Outcome[], dryRun: boolean): void => {
    const installed = outcomes.filter(outcome => outcome.status === "installed")
    const planned = outcomes.filter(outcome => outcome.status === "planned")
    const present = outcomes.filter(outcome => outcome.status === "already-installed")
    const failures = outcomes.filter(
        outcome => outcome.status === "failed" || outcome.status === "blocked",
    )

    console.log(
        colors.green(
            dryRun
                ? `\n${planned.length} installable(s) to install, ${present.length} already present.`
                : `\n${installed.length} installable(s) installed, ${present.length} already present.`,
        ),
    )
    if (failures.length === 0) {
        return
    }

    console.log(colors.red(`${failures.length} installable(s) not installed:`))
    for (const failure of failures) {
        console.log(
            colors.red(`  ${installableId(failure.installable)}: ${failure.detail}`),
        )
    }
    process.exitCode = 1
}

/**
 * @description Builds the plan of this platform, runs its steps in order, then reports the outcome.
 */
const main = async (): Promise<void> => {
    const { dryRun } = parseCliOptions(argv)
    const plan = await buildInstallPlan(platform)

    if (!plan.success) {
        console.error(colors.red(plan.error.message))
        process.exitCode = 1
        return
    }

    const systemOutcomes = reportSystemApplications(plan.value.systemApplications)
    const systemFailures = systemOutcomes.filter(outcome => outcome.status === "failed")

    const failed = new Set(
        systemFailures.map(outcome => installableKey(outcome.installable)),
    )
    const outcomes: Outcome[] = [...systemFailures]

    for (const step of plan.value.steps) {
        const stepOutcomes = await runStep(step, failed, dryRun)
        for (const outcome of stepOutcomes) {
            if (outcome.status === "failed" || outcome.status === "blocked") {
                failed.add(installableKey(outcome.installable))
            }
        }
        outcomes.push(...stepOutcomes)
    }

    reportOutcomes(outcomes, dryRun)
}

void main()
