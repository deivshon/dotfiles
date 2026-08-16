import process, { argv } from "node:process"

import { colors } from "es-toolkit/server"

import { parseCliOptions } from "./cli"
import { applyConfig } from "./configs/configs"
import { buildConfigPlan } from "./configs/plan"
import type { ConfigError, InstallError } from "./errors"
import { installableId, installableKey } from "./installables/installables"
import { buildInstallPlan } from "./installs/plan"
import type { InstallStep } from "./installs/plan"
import {
    nodesOfStep,
    reportBaseSystem,
    reportBaseSystemFailure,
    reportBlocked,
    reportConfigApplied,
    reportConfigFailure,
    reportConfigSkipped,
    reportConfigsStart,
    reportDryRun,
    reportInstallFailure,
    reportInstalled,
    reportNothingToInstall,
    reportPlan,
    reportPlatform,
    reportStepStart,
} from "./report"
import { platform } from "./shared/platform"
import type { Result } from "./shared/result"
import type { ConfigResult, ConfigTarget } from "./types/configs"
import type { Installable, InstallableKey } from "./types/installables"

type OutcomeStatus = "installed" | "already-installed" | "failed" | "blocked"

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

/**
 * @param node Node to install
 * @param failed Keys of the installables that did not install
 * @description Returns the dependencies of the node that did not install.
 */
const blockersOf = (node: TargetNode, failed: Set<InstallableKey>): Installable[] =>
    node.requires.filter(installable => failed.has(installableKey(installable)))

/**
 * @param node Node that the plan skips
 * @description Returns the outcome of a node that is present already.
 */
const toAlreadyInstalled = (node: TargetNode): Outcome => ({
    installable: node.installable,
    status: "already-installed",
    detail: "",
})

/**
 * @param node Node that a failed dependency holds back
 * @param blockers Dependencies that did not install
 * @description Reports a blocked node, and returns its outcome.
 */
const toBlocked = (node: TargetNode, blockers: Installable[]): Outcome => {
    reportBlocked(blockers, [node.installable])

    return {
        installable: node.installable,
        status: "blocked",
        detail: `The dependencies failed: ${blockers.map(installableId).join(", ")}`,
    }
}

/**
 * @param node Node of the step
 * @param failed Keys of the installables that did not install
 * @description True when the node is absent and no failed dependency blocks it.
 */
const isRunnable = (node: TargetNode, failed: Set<InstallableKey>): boolean =>
    !node.skip && blockersOf(node, failed).length === 0

/**
 * @param install Command that installs the nodes
 * @param nodes Nodes that the command covers
 * @description Runs one install command, and returns the outcome of every node it covers.
 */
const runInstall = async (
    install: () => Promise<Result<void, InstallError>>,
    nodes: TargetNode[],
): Promise<Outcome[]> => {
    const installables = nodes.map(node => node.installable)
    const result = await install()

    if (!result.success) {
        reportInstallFailure(installables, result.error.message)
        return nodes.map((node): Outcome => ({
            installable: node.installable,
            status: "failed",
            detail: result.error.message,
        }))
    }

    reportInstalled(installables)
    return nodes.map((node): Outcome => ({
        installable: node.installable,
        status: "installed",
        detail: "",
    }))
}

/**
 * @param step Step of the plan
 * @param failed Keys of the installables that did not install
 * @description Runs one step of the plan, and returns the outcome of every absent node.
 * @remarks Reports the nodes that a failed dependency blocks, and leaves them out of the command.
 */
const runStep = async (
    step: InstallStep,
    failed: Set<InstallableKey>,
): Promise<Outcome[]> => {
    const nodes = nodesOfStep(step)
    const blocked = nodes
        .filter(node => !node.skip)
        .map(node => ({ node, blockers: blockersOf(node, failed) }))
        .filter(entry => entry.blockers.length > 0)
        .map(entry => toBlocked(entry.node, entry.blockers))

    const runnable = nodes.filter(node => isRunnable(node, failed))
    if (runnable.length === 0) {
        return blocked
    }

    return [
        ...blocked,
        ...(await runInstall(
            step.type === "custom"
                ? step.node.install
                : step.install(
                      step.nodes
                          .filter(node => isRunnable(node, failed))
                          .map(node => node.packageName),
                  ),
            runnable,
        )),
    ]
}

/**
 * @param outcomes Outcome of every node of the plan
 * @description Reports the totals of the run, and sets the exit code on a failure.
 */
const reportOutcomes = (outcomes: Outcome[]): void => {
    const installed = outcomes.filter(outcome => outcome.status === "installed")
    const present = outcomes.filter(outcome => outcome.status === "already-installed")
    const failures = outcomes.filter(
        outcome => outcome.status === "failed" || outcome.status === "blocked",
    )

    console.log(
        colors.green(
            `\n${installed.length} installable(s) installed, ${present.length} already present.`,
        ),
    )
    if (failures.length === 0) {
        return
    }

    console.log(colors.red(`${failures.length} installable(s) not installed:`))
    console.log(
        failures
            .map(failure =>
                colors.red(`  ${installableId(failure.installable)}: ${failure.detail}`),
            )
            .join("\n"),
    )
    process.exitCode = 1
}

/**
 * @param targets Config files of the plan
 * @param failed Keys of the installables that did not install
 * @description Copies every config file of an application that is present, and returns the count of failures.
 * @remarks Leaves out the config files of an application that did not install.
 */
const runConfigs = async (
    targets: ConfigTarget[],
    failed: Set<InstallableKey>,
): Promise<number> => {
    const remaining = targets.filter(target => !target.skip)
    const skipped = remaining.filter(target =>
        failed.has(installableKey(target.installable)),
    )
    const pending = remaining.filter(
        target => !failed.has(installableKey(target.installable)),
    )
    if (remaining.length === 0) {
        return 0
    }

    reportConfigsStart()
    if (skipped.length > 0) {
        reportConfigSkipped(skipped)
    }

    const results: Array<Result<ConfigResult, ConfigError>> = []
    for (const target of pending) {
        const result = await applyConfig(target)
        if (result.success) {
            reportConfigApplied(result.value)
        } else {
            reportConfigFailure(target, result.error.message)
        }
        results.push(result)
    }

    return skipped.length + results.filter(result => !result.success).length
}

/**
 * @description Builds the plan of this platform, runs its steps in order, then reports the outcome.
 */
const main = async (): Promise<void> => {
    const { dryRun, configs } = parseCliOptions(argv)

    reportPlatform(platform)

    const plan = await buildInstallPlan(platform)
    if (!plan.success) {
        console.error(colors.red(plan.error.message))
        process.exitCode = 1
        return
    }

    reportBaseSystem(plan.value.systemApplications)
    const missing = plan.value.systemApplications.filter(node => !node.skip)
    if (missing.length > 0) {
        reportBaseSystemFailure(missing)
        process.exitCode = 1
        return
    }

    const configTargets = configs ? await buildConfigPlan(platform) : null
    reportPlan(plan.value.steps, configTargets)

    if (dryRun) {
        reportDryRun()
        return
    }

    const pendingSteps = plan.value.steps.filter(step =>
        nodesOfStep(step).some(node => !node.skip),
    )
    const failed = new Set<InstallableKey>()
    const outcomes: Outcome[] = plan.value.steps
        .flatMap(nodesOfStep)
        .filter(node => node.skip)
        .map(toAlreadyInstalled)

    for (const [index, step] of pendingSteps.entries()) {
        reportStepStart(step, index, pendingSteps.length)
        const stepOutcomes = await runStep(step, failed)
        for (const outcome of stepOutcomes) {
            if (outcome.status === "failed" || outcome.status === "blocked") {
                failed.add(installableKey(outcome.installable))
            }
        }
        outcomes.push(...stepOutcomes)
    }

    if (pendingSteps.length === 0) {
        reportNothingToInstall()
    } else {
        reportOutcomes(outcomes)
    }

    if (configTargets === null) {
        return
    }

    if ((await runConfigs(configTargets, failed)) > 0) {
        process.exitCode = 1
    }
}

void main()
