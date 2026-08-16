import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import type { InstallError } from "./errors"
import type { CustomInstallStep, InstallPlan, PackageInstallStep } from "./installs/plan"
import { Result } from "./shared/result"
import type { ConfigTarget } from "./types/configs"
import type { Installable } from "./types/installables"

const parseCliOptions = vi.hoisted(() => vi.fn())
const buildInstallPlan = vi.hoisted(() => vi.fn())
const buildConfigPlan = vi.hoisted(() => vi.fn())
const applyConfig = vi.hoisted(() => vi.fn())
const reports = vi.hoisted(() => ({
    reportBaseSystem: vi.fn(),
    reportBaseSystemFailure: vi.fn(),
    reportBlocked: vi.fn(),
    reportConfigApplied: vi.fn(),
    reportConfigFailure: vi.fn(),
    reportConfigSkipped: vi.fn(),
    reportConfigsStart: vi.fn(),
    reportDryRun: vi.fn(),
    reportInstallFailure: vi.fn(),
    reportInstalled: vi.fn(),
    reportNothingToInstall: vi.fn(),
    reportPlan: vi.fn(),
    reportPlatform: vi.fn(),
    reportStepStart: vi.fn(),
}))

vi.mock("./cli", () => ({ parseCliOptions }))
vi.mock("./installs/plan", () => ({ buildInstallPlan }))
vi.mock("./configs/plan", () => ({ buildConfigPlan }))
vi.mock("./configs/configs", () => ({ applyConfig }))
vi.mock("./shared/platform", () => ({ platform: "arch-linux" }))
vi.mock("./report", async importOriginal => ({
    ...(await importOriginal<typeof import("./report")>()),
    ...reports,
}))

const tick = (): Promise<void> =>
    new Promise(resolve => {
        setImmediate(resolve)
    })

/** @description Runs the entry point of the command, and waits for it to settle. */
const runMain = async (): Promise<void> => {
    vi.resetModules()
    await import("./index")
    await Array.from({ length: 20 }).reduce<Promise<void>>(
        previous => previous.then(tick),
        Promise.resolve(),
    )
}

const packageStep = (
    entries: Array<{
        installable: Installable
        skip?: boolean
        requires?: Installable[]
    }>,
) => {
    const run = vi.fn(() => Promise.resolve(Result.ok(undefined)))
    const step: PackageInstallStep = {
        type: "package",
        channel: "arch-standard",
        nodes: entries.map(entry => ({
            type: "package",
            channel: "arch-standard",
            packageName: entry.installable[1],
            installable: entry.installable,
            requires: entry.requires ?? [],
            skip: entry.skip ?? false,
        })),
        install: vi.fn(() => run),
    }
    return { step, run }
}

const customStep = (
    installable: Installable,
    options: {
        skip?: boolean
        requires?: Installable[]
        result?: Result<void, InstallError>
    } = {},
) => {
    const run = vi.fn(() => Promise.resolve(options.result ?? Result.ok(undefined)))
    const step: CustomInstallStep = {
        type: "custom",
        node: {
            type: "custom",
            installable,
            requires: options.requires ?? [],
            skip: options.skip ?? false,
            install: run,
        },
    }
    return { step, run }
}

const plan = (steps: InstallPlan["steps"], systemSkip = true): InstallPlan => ({
    systemApplications: [
        {
            type: "system",
            installable: ["application", "pacman"],
            requires: [],
            skip: systemSkip,
        },
    ],
    steps,
})

const configTarget = (
    destination: string,
    overrides: Partial<ConfigTarget> = {},
): ConfigTarget => ({
    type: "file-copy",
    source: "/repo/files/app/config",
    destination,
    installable: ["application", "ghostty"],
    skip: false,
    ...overrides,
})

const commandFailed = {
    type: "command-failed" as const,
    command: "pacman -S git",
    exitCode: 1,
    output: "",
    message: "The install failed",
}

beforeEach(() => {
    vi.spyOn(console, "log").mockImplementation(() => undefined)
    vi.spyOn(console, "error").mockImplementation(() => undefined)
    parseCliOptions.mockReturnValue({ dryRun: false, configs: true })
    buildConfigPlan.mockResolvedValue([])
    applyConfig.mockResolvedValue(Result.ok({ status: "copied", backupPath: null }))
    for (const report of Object.values(reports)) {
        report.mockClear()
    }
})

afterEach(() => {
    process.exitCode = undefined
})

describe("the platform and the plan", () => {
    it("reports the platform of the machine", async () => {
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))

        await runMain()

        expect(reports.reportPlatform).toHaveBeenCalledExactlyOnceWith("arch-linux")
        expect(buildInstallPlan).toHaveBeenCalledExactlyOnceWith("arch-linux")
    })

    it("reports the error of a plan that did not build", async () => {
        buildInstallPlan.mockResolvedValue(
            Result.err({ type: "dependency-cycle", path: [], message: "A cycle" }),
        )

        await runMain()

        expect(process.exitCode).toBe(1)
        expect(reports.reportPlan).not.toHaveBeenCalled()
    })

    it("stops when the base system misses an application", async () => {
        const { step, run } = packageStep([{ installable: ["application", "git"] }])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step], false)))

        await runMain()

        expect(reports.reportBaseSystemFailure).toHaveBeenCalledOnce()
        expect(process.exitCode).toBe(1)
        expect(run).not.toHaveBeenCalled()
    })

    it("reports the base system before the plan", async () => {
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))

        await runMain()

        expect(reports.reportBaseSystem).toHaveBeenCalledOnce()
        expect(reports.reportPlan).toHaveBeenCalledOnce()
    })
})

describe("the dry run", () => {
    it("runs no install", async () => {
        const { step, run } = packageStep([{ installable: ["application", "git"] }])
        parseCliOptions.mockReturnValue({ dryRun: true, configs: true })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(reports.reportDryRun).toHaveBeenCalledOnce()
        expect(run).not.toHaveBeenCalled()
        expect(applyConfig).not.toHaveBeenCalled()
        expect(process.exitCode).toBeUndefined()
    })

    it("reports the plan of the config files", async () => {
        parseCliOptions.mockReturnValue({ dryRun: true, configs: true })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))
        buildConfigPlan.mockResolvedValue([configTarget("/home/user/a")])

        await runMain()

        expect(reports.reportPlan).toHaveBeenCalledExactlyOnceWith(
            [],
            [configTarget("/home/user/a")],
        )
    })
})

describe("the config flag", () => {
    it("builds no config plan when the flag is off", async () => {
        parseCliOptions.mockReturnValue({ dryRun: false, configs: false })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))

        await runMain()

        expect(buildConfigPlan).not.toHaveBeenCalled()
        expect(reports.reportPlan).toHaveBeenCalledExactlyOnceWith([], null)
        expect(applyConfig).not.toHaveBeenCalled()
    })
})

describe("the install steps", () => {
    it("runs a package step with the names of the absent packages alone", async () => {
        const { step, run } = packageStep([
            { installable: ["application", "git"] },
            { installable: ["application", "bat"], skip: true },
        ])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(step.install).toHaveBeenCalledExactlyOnceWith(["git"])
        expect(run).toHaveBeenCalledOnce()
        expect(reports.reportInstalled).toHaveBeenCalledExactlyOnceWith([
            ["application", "git"],
        ])
    })

    it("runs a custom step through its own install", async () => {
        const { step, run } = customStep(["application", "ccommit"])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(run).toHaveBeenCalledOnce()
    })

    it("leaves out a step where every node is present", async () => {
        const { step, run } = packageStep([
            { installable: ["application", "git"], skip: true },
        ])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(run).not.toHaveBeenCalled()
        expect(reports.reportNothingToInstall).toHaveBeenCalledOnce()
        expect(reports.reportStepStart).not.toHaveBeenCalled()
    })

    it("numbers the steps that it runs", async () => {
        const first = packageStep([{ installable: ["application", "git"] }])
        const present = packageStep([{ installable: ["application", "bat"], skip: true }])
        const last = customStep(["application", "ccommit"])
        buildInstallPlan.mockResolvedValue(
            Result.ok(plan([first.step, present.step, last.step])),
        )

        await runMain()

        expect(reports.reportStepStart.mock.calls).toEqual([
            [first.step, 0, 2],
            [last.step, 1, 2],
        ])
    })

    it("reports the error of an install that failed", async () => {
        const { step, run } = customStep(["application", "ccommit"], {
            result: Result.err(commandFailed),
        })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(run).toHaveBeenCalledOnce()
        expect(reports.reportInstallFailure).toHaveBeenCalledExactlyOnceWith(
            [["application", "ccommit"]],
            "The install failed",
        )
        expect(process.exitCode).toBe(1)
    })

    it("blocks an installable whose dependency failed", async () => {
        const first = customStep(["application", "git"], {
            result: Result.err(commandFailed),
        })
        const second = customStep(["application", "ccommit"], {
            requires: [["application", "git"]],
        })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([first.step, second.step])))

        await runMain()

        expect(second.run).not.toHaveBeenCalled()
        expect(reports.reportBlocked).toHaveBeenCalledExactlyOnceWith(
            [["application", "git"]],
            [["application", "ccommit"]],
        )
        expect(process.exitCode).toBe(1)
    })

    it("blocks an installable through a chain of dependencies", async () => {
        const first = customStep(["application", "git"], {
            result: Result.err(commandFailed),
        })
        const second = customStep(["application", "ccommit"], {
            requires: [["application", "git"]],
        })
        const third = customStep(["toolchain", "rust-stable"], {
            requires: [["application", "ccommit"]],
        })
        buildInstallPlan.mockResolvedValue(
            Result.ok(plan([first.step, second.step, third.step])),
        )

        await runMain()

        expect(second.run).not.toHaveBeenCalled()
        expect(third.run).not.toHaveBeenCalled()
        expect(reports.reportBlocked).toHaveBeenCalledTimes(2)
    })

    it("keeps the packages of a step that no failure blocks", async () => {
        const first = customStep(["application", "git"], {
            result: Result.err(commandFailed),
        })
        const second = packageStep([
            {
                installable: ["application", "ccommit"],
                requires: [["application", "git"]],
            },
            { installable: ["application", "bat"] },
        ])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([first.step, second.step])))

        await runMain()

        expect(second.step.install).toHaveBeenCalledExactlyOnceWith(["bat"])
        expect(second.run).toHaveBeenCalledOnce()
    })

    it("sets no exit code when every install works", async () => {
        const { step } = packageStep([{ installable: ["application", "git"] }])
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))

        await runMain()

        expect(process.exitCode).toBeUndefined()
    })
})

describe("the config files", () => {
    it("copies every config file that the destination does not hold", async () => {
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))
        buildConfigPlan.mockResolvedValue([
            configTarget("/home/user/a"),
            configTarget("/home/user/b", { skip: true }),
        ])

        await runMain()

        expect(applyConfig).toHaveBeenCalledExactlyOnceWith(configTarget("/home/user/a"))
        expect(reports.reportConfigsStart).toHaveBeenCalledOnce()
        expect(reports.reportConfigApplied).toHaveBeenCalledOnce()
    })

    it("opens no config section when every destination is current", async () => {
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))
        buildConfigPlan.mockResolvedValue([configTarget("/home/user/a", { skip: true })])

        await runMain()

        expect(reports.reportConfigsStart).not.toHaveBeenCalled()
        expect(applyConfig).not.toHaveBeenCalled()
    })

    it("leaves out the config files of an application that did not install", async () => {
        const { step } = customStep(["application", "ghostty"], {
            result: Result.err(commandFailed),
        })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))
        buildConfigPlan.mockResolvedValue([configTarget("/home/user/a")])

        await runMain()

        expect(applyConfig).not.toHaveBeenCalled()
        expect(reports.reportConfigSkipped).toHaveBeenCalledExactlyOnceWith([
            configTarget("/home/user/a"),
        ])
        expect(process.exitCode).toBe(1)
    })

    it("reports the error of a config file that did not reach its destination", async () => {
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))
        buildConfigPlan.mockResolvedValue([configTarget("/home/user/a")])
        applyConfig.mockResolvedValue(
            Result.err({
                type: "file-system-failed",
                path: "/home/user/a",
                cause: null,
                message: "The file was not written",
            }),
        )

        await runMain()

        expect(reports.reportConfigFailure).toHaveBeenCalledExactlyOnceWith(
            configTarget("/home/user/a"),
            "The file was not written",
        )
        expect(process.exitCode).toBe(1)
    })

    it("copies the config files one after the other", async () => {
        const order: string[] = []
        buildInstallPlan.mockResolvedValue(Result.ok(plan([])))
        buildConfigPlan.mockResolvedValue([
            configTarget("/home/user/a"),
            configTarget("/home/user/b"),
        ])
        applyConfig.mockImplementation(async (target: ConfigTarget) => {
            order.push(`start ${target.destination}`)
            await tick()
            order.push(`end ${target.destination}`)
            return Result.ok({ target, status: "copied", backupPath: null })
        })

        await runMain()

        expect(order).toEqual([
            "start /home/user/a",
            "end /home/user/a",
            "start /home/user/b",
            "end /home/user/b",
        ])
    })

    it("copies the config files after the installs", async () => {
        const order: string[] = []
        const { step, run } = customStep(["application", "ghostty"])
        run.mockImplementation(async () => {
            order.push("install")
            return Result.ok(undefined)
        })
        applyConfig.mockImplementation(async (target: ConfigTarget) => {
            order.push("config")
            return Result.ok({ target, status: "copied", backupPath: null })
        })
        buildInstallPlan.mockResolvedValue(Result.ok(plan([step])))
        buildConfigPlan.mockResolvedValue([configTarget("/home/user/a")])

        await runMain()

        expect(order).toEqual(["install", "config"])
    })
})
