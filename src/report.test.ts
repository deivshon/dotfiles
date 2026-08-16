import { beforeEach, describe, expect, it, vi } from "vitest"

import type {
    CustomInstallStep,
    PackageInstallStep,
    SystemPlanNode,
} from "./installs/plan"
import {
    nodesOfStep,
    reportBaseSystem,
    reportBaseSystemFailure,
    reportBlocked,
    reportCommand,
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
    stepLabel,
} from "./report"
import { Result } from "./shared/result"
import type { ConfigTarget } from "./types/configs"
import type { Installable } from "./types/installables"
import type { Platform } from "./types/platforms"

const ANSI = /\[\d+m/gu

const logged = (): string =>
    vi
        .mocked(console.log)
        .mock.calls.map(call => call.join(" "))
        .join("\n")
        .replaceAll(ANSI, "")

const errored = (): string =>
    vi
        .mocked(console.error)
        .mock.calls.map(call => call.join(" "))
        .join("\n")
        .replaceAll(ANSI, "")

const systemNode = (id: "pacman" | "makepkg", skip: boolean): SystemPlanNode => ({
    type: "system",
    installable: ["application", id],
    requires: [],
    skip,
})

const packageStep = (installables: Installable[], skip = false): PackageInstallStep => ({
    type: "package",
    channel: "arch-standard",
    nodes: installables.map(installable => ({
        type: "package",
        channel: "arch-standard",
        packageName: installable[1],
        installable,
        requires: [],
        skip,
    })),
    install: () => () => Promise.resolve(Result.ok(undefined)),
})

const customStep = (installable: Installable, skip = false): CustomInstallStep => ({
    type: "custom",
    node: {
        type: "custom",
        installable,
        requires: [],
        skip,
        install: () => Promise.resolve(Result.ok(undefined)),
    },
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

beforeEach(() => {
    vi.spyOn(console, "log").mockImplementation(() => undefined)
    vi.spyOn(console, "error").mockImplementation(() => undefined)
})

describe("nodesOfStep", () => {
    it("returns the single node of a custom step", () => {
        const step = customStep(["application", "ccommit"])

        expect(nodesOfStep(step)).toEqual([step.node])
    })

    it("returns every node of a package step", () => {
        const step = packageStep([
            ["application", "git"],
            ["application", "bat"],
        ])

        expect(nodesOfStep(step)).toEqual(step.nodes)
    })

    it("returns an empty list for a package step with no node", () => {
        expect(nodesOfStep(packageStep([]))).toEqual([])
    })
})

describe("stepLabel", () => {
    it.each([
        { channel: "arch-standard" as const, label: "pacman" },
        { channel: "arch-aur" as const, label: "paru" },
        { channel: "brew-formula" as const, label: "brew" },
        { channel: "brew-cask" as const, label: "brew --cask" },
    ])("names the $channel channel $label", ({ channel, label }) => {
        expect(stepLabel({ ...packageStep([]), channel })).toBe(label)
    })

    it("names a custom step after its installable", () => {
        expect(stepLabel(customStep(["application", "ccommit"]))).toBe(
            "custom install of ccommit",
        )
    })
})

describe("reportPlatform", () => {
    it.each([
        { platform: "arch-linux" as Platform, label: "Arch Linux" },
        { platform: "mac-os" as Platform, label: "macOS" },
        { platform: "windows" as Platform, label: "Windows" },
    ])("names $platform as $label", ({ platform, label }) => {
        reportPlatform(platform)

        expect(logged()).toContain(`Platform: ${label}`)
    })
})

describe("reportBaseSystem", () => {
    it("marks a present application with a check", () => {
        reportBaseSystem([systemNode("pacman", true)])

        expect(logged()).toContain("✓ pacman")
    })

    it("marks an absent application with a cross", () => {
        reportBaseSystem([systemNode("pacman", false)])

        expect(logged()).toContain("✗ pacman")
    })

    it("lists every application", () => {
        reportBaseSystem([systemNode("pacman", true), systemNode("makepkg", false)])

        const output = logged()
        expect(output).toContain("✓ pacman")
        expect(output).toContain("✗ makepkg")
    })
})

describe("reportBaseSystemFailure", () => {
    it("names every absent application and the next move", () => {
        reportBaseSystemFailure([
            systemNode("pacman", false),
            systemNode("makepkg", false),
        ])

        const output = errored()
        expect(output).toContain("The base system does not provide: pacman, makepkg")
        expect(output).toContain(
            "Install these applications, then run this command again.",
        )
    })
})

describe("reportPlan", () => {
    it("counts the installables to install and the ones present", () => {
        reportPlan(
            [
                packageStep([["application", "git"]], false),
                packageStep([["application", "bat"]], true),
            ],
            [],
        )

        expect(logged()).toContain("installables: 1 to install, 1 already present")
    })

    it("counts the config files to copy and the ones current", () => {
        reportPlan(
            [],
            [configTarget("/home/user/a"), configTarget("/home/user/b", { skip: true })],
        )

        expect(logged()).toContain("configs: 1 to copy, 1 already current")
    })

    it("reports the config files as skipped when the run leaves them out", () => {
        reportPlan([], null)

        expect(logged()).toContain("configs: skipped")
    })

    it("groups the installables by kind, in a fixed order", () => {
        reportPlan(
            [
                packageStep([
                    ["extension", "oxc-vscode"],
                    ["application", "git"],
                    ["toolchain", "rust-stable"],
                    ["library", "base-devel"],
                ]),
            ],
            [],
        )
        const output = logged()

        expect(output.indexOf("applications")).toBeLessThan(output.indexOf("libraries"))
        expect(output.indexOf("libraries")).toBeLessThan(output.indexOf("toolchains"))
        expect(output.indexOf("toolchains")).toBeLessThan(output.indexOf("extensions"))
    })

    it("leaves out a kind that the plan does not cover", () => {
        reportPlan([packageStep([["application", "git"]])], [])

        expect(logged()).not.toContain("libraries")
    })

    it("marks an installable that is present already", () => {
        reportPlan([packageStep([["application", "git"]], true)], [])

        expect(logged()).toContain("• git (already installed)")
    })

    it("puts the config files under their installable", () => {
        reportPlan(
            [packageStep([["application", "ghostty"]])],
            [configTarget("/home/user/.config/ghostty/config.ghostty")],
        )
        const output = logged()

        expect(output).toContain("• ghostty")
        expect(output.indexOf("• ghostty")).toBeLessThan(
            output.indexOf("◦ /home/user/.config/ghostty/config.ghostty"),
        )
    })

    it("marks a merge in the line of the config file", () => {
        reportPlan(
            [packageStep([["application", "ghostty"]])],
            [configTarget("/home/user/a", { type: "json-merge" })],
        )

        expect(logged()).toContain("◦ /home/user/a (merge)")
    })

    it("marks a config file that is current already", () => {
        reportPlan(
            [packageStep([["application", "ghostty"]])],
            [configTarget("/home/user/a", { skip: true })],
        )

        expect(logged()).toContain("◦ /home/user/a (already current)")
    })

    it("collects the config files of an installable that no step holds", () => {
        reportPlan([], [configTarget("/home/user/a")])
        const output = logged()

        expect(output).toContain("configs")
        expect(output).toContain("• ghostty")
        expect(output).toContain("◦ /home/user/a")
    })

    it("groups the loose config files of one installable under one line", () => {
        reportPlan([], [configTarget("/home/user/a"), configTarget("/home/user/b")])
        const output = logged()

        expect(output.match(/• ghostty/gu)).toHaveLength(1)
    })

    it("leaves the loose group out when every config file has a node", () => {
        reportPlan(
            [packageStep([["application", "ghostty"]])],
            [configTarget("/home/user/a")],
        )

        expect(logged()).not.toContain("  configs\n")
    })
})

describe("reportStepStart", () => {
    it("numbers the step from one", () => {
        reportStepStart(packageStep([["application", "git"]]), 0, 3)

        expect(logged()).toContain("Step 1/3 — pacman")
    })

    it("names the last step with the total", () => {
        reportStepStart(customStep(["application", "ccommit"]), 2, 3)

        expect(logged()).toContain("Step 3/3 — custom install of ccommit")
    })
})

describe("install outcome reports", () => {
    it("reports nothing to install", () => {
        reportNothingToInstall()

        expect(logged()).toContain("Nothing to install.")
    })

    it("reports the dry run", () => {
        reportDryRun()

        expect(logged()).toContain("Dry run: no install ran.")
    })

    it("names the installables that a failed dependency blocks", () => {
        reportBlocked(
            [["application", "git"]],
            [
                ["application", "ccommit"],
                ["application", "paru"],
            ],
        )

        expect(logged()).toContain("⊘ ccommit, paru: the dependencies failed (git)")
    })

    it("names the installables of a command that worked", () => {
        reportInstalled([
            ["application", "git"],
            ["application", "bat"],
        ])

        expect(logged()).toContain("✓ git, bat")
    })

    it("names the installables and the error of a command that failed", () => {
        reportInstallFailure([["application", "git"]], "The command exited with code 1")

        expect(logged()).toContain("✗ git: The command exited with code 1")
    })
})

describe("config reports", () => {
    it("opens the config section", () => {
        reportConfigsStart()

        expect(logged()).toContain("Configs")
    })

    it("reports a config file that the run copied", () => {
        reportConfigApplied({
            target: configTarget("/home/user/a"),
            status: "copied",
            backupPath: null,
        })

        expect(logged()).toContain("✓ /home/user/a")
    })

    it("names the backup of a config file that the run replaced", () => {
        reportConfigApplied({
            target: configTarget("/home/user/a"),
            status: "replaced",
            backupPath: "/home/user/a.bkp-1",
        })
        const output = logged()

        expect(output).toContain("✓ /home/user/a")
        expect(output).toContain("backup: /home/user/a.bkp-1")
    })

    it("reports a config file that holds its content already", () => {
        reportConfigApplied({
            target: configTarget("/home/user/a"),
            status: "unchanged",
            backupPath: null,
        })
        const output = logged()

        expect(output).toContain("= /home/user/a (already current)")
        expect(output).not.toContain("backup")
    })

    it("names the config file and the error of a copy that failed", () => {
        reportConfigFailure(configTarget("/home/user/a"), "The file was not read")

        expect(logged()).toContain("✗ /home/user/a: The file was not read")
    })

    it("names the config files that the failed application holds back", () => {
        reportConfigSkipped([configTarget("/home/user/a"), configTarget("/home/user/b")])

        expect(logged()).toContain(
            "⊘ /home/user/a, /home/user/b: the application did not install",
        )
    })
})

describe("reportCommand", () => {
    it("echoes the command and its arguments", () => {
        reportCommand("sudo", ["pacman", "-S", "--needed", "git"])

        expect(logged()).toContain("$ sudo pacman -S --needed git")
    })

    it("echoes a command that takes no argument", () => {
        reportCommand("brew", [])

        expect(logged()).toContain("$ brew")
    })
})
