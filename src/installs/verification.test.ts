import { beforeEach, describe, expect, it, vi } from "vitest"

import { Result } from "../shared/result"
import type { Platform } from "../types/platforms"

const runQuietly = vi.hoisted(() => vi.fn())
const commandSucceeds = vi.hoisted(() => vi.fn())

vi.mock("../process", () => ({ runQuietly, commandSucceeds }))

const {
    isAurArchLinuxPackageInstalled,
    isBrewCaskPackageInstalled,
    isBrewFormulaePackageInstalled,
    isExecutableInPath,
    isRustupToolchainInstalled,
    isStandardArchLinuxPackageInstalled,
    isVsCodeExtensionInstalled,
    listAurArchLinuxPackages,
    listBrewCaskPackages,
    listBrewFormulaePackages,
    listRustupToolchains,
    listStandardArchLinuxPackages,
    listVsCodeExtensions,
} = await import("./verification")

const commandNotRun = {
    type: "command-not-run" as const,
    command: "pacman -Qnq",
    cause: new Error("ENOENT"),
    message: "The command failed",
}

beforeEach(() => {
    runQuietly.mockReset()
    commandSucceeds.mockReset()
})

describe("list commands", () => {
    const listCases = [
        {
            name: "standard Arch Linux packages",
            list: listStandardArchLinuxPackages,
            command: "pacman",
            args: ["-Qnq"],
        },
        {
            name: "AUR packages",
            list: listAurArchLinuxPackages,
            command: "pacman",
            args: ["-Qmq"],
        },
        {
            name: "Homebrew formulae",
            list: listBrewFormulaePackages,
            command: "brew",
            args: ["list", "--formula", "-1"],
        },
        {
            name: "Homebrew casks",
            list: listBrewCaskPackages,
            command: "brew",
            args: ["list", "--cask", "-1"],
        },
        {
            name: "Rust toolchains",
            list: listRustupToolchains,
            command: "rustup",
            args: ["toolchain", "list"],
        },
        {
            name: "Visual Studio Code extensions",
            list: listVsCodeExtensions,
            command: "code",
            args: ["--list-extensions"],
        },
    ]

    it.each(listCases)(
        "reads the $name with the right command",
        async ({ list, command, args }) => {
            runQuietly.mockResolvedValue(Result.ok(""))

            await list()

            expect(runQuietly).toHaveBeenCalledExactlyOnceWith(command, args)
        },
    )

    it("splits the output into one name per line", async () => {
        runQuietly.mockResolvedValue(Result.ok("git\nbat\neza\n"))

        await expect(listStandardArchLinuxPackages()).resolves.toEqual({
            success: true,
            value: ["git", "bat", "eza"],
        })
    })

    it("trims every line and drops the empty ones", async () => {
        runQuietly.mockResolvedValue(Result.ok("  git  \n\n\t\nbat\n   \n"))

        await expect(listStandardArchLinuxPackages()).resolves.toEqual({
            success: true,
            value: ["git", "bat"],
        })
    })

    it("returns an empty list for an empty output", async () => {
        runQuietly.mockResolvedValue(Result.ok(""))

        await expect(listStandardArchLinuxPackages()).resolves.toEqual({
            success: true,
            value: [],
        })
    })

    it("keeps the error of a command that failed", async () => {
        runQuietly.mockResolvedValue(Result.err(commandNotRun))

        await expect(listStandardArchLinuxPackages()).resolves.toEqual({
            success: false,
            error: commandNotRun,
        })
    })
})

describe("package checks", () => {
    const checkCases = [
        {
            name: "a standard Arch Linux package",
            check: isStandardArchLinuxPackageInstalled,
            command: "pacman",
            args: ["-Qnq"],
        },
        {
            name: "an AUR package",
            check: isAurArchLinuxPackageInstalled,
            command: "pacman",
            args: ["-Qmq"],
        },
        {
            name: "a Homebrew formula",
            check: isBrewFormulaePackageInstalled,
            command: "brew",
            args: ["list", "--formula", "-1"],
        },
        {
            name: "a Homebrew cask",
            check: isBrewCaskPackageInstalled,
            command: "brew",
            args: ["list", "--cask", "-1"],
        },
        {
            name: "a Visual Studio Code extension",
            check: isVsCodeExtensionInstalled,
            command: "code",
            args: ["--list-extensions"],
        },
    ]

    it.each(checkCases)(
        "finds $name in its own list",
        async ({ check, command, args }) => {
            runQuietly.mockResolvedValue(Result.ok("target\n"))

            await expect(check("target")()).resolves.toEqual({
                success: true,
                value: true,
            })
            expect(runQuietly).toHaveBeenCalledExactlyOnceWith(command, args)
        },
    )

    it("returns false when the list leaves the package out", async () => {
        runQuietly.mockResolvedValue(Result.ok("git\nbat\n"))

        await expect(isStandardArchLinuxPackageInstalled("eza")()).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("matches the whole name and not a prefix", async () => {
        runQuietly.mockResolvedValue(Result.ok("base-devel\n"))

        await expect(isStandardArchLinuxPackageInstalled("base")()).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("does not read the list before the call", () => {
        isStandardArchLinuxPackageInstalled("git")

        expect(runQuietly).not.toHaveBeenCalled()
    })

    it("reads the list again on every call", async () => {
        runQuietly.mockResolvedValue(Result.ok("git\n"))
        const check = isStandardArchLinuxPackageInstalled("git")

        await check()
        await check()

        expect(runQuietly).toHaveBeenCalledTimes(2)
    })

    it("keeps the error of a list that failed", async () => {
        runQuietly.mockResolvedValue(Result.err(commandNotRun))

        await expect(isStandardArchLinuxPackageInstalled("git")()).resolves.toEqual({
            success: false,
            error: commandNotRun,
        })
    })
})

describe("isRustupToolchainInstalled", () => {
    it("matches the channel as a prefix of the target triple", async () => {
        runQuietly.mockResolvedValue(
            Result.ok("stable-x86_64-unknown-linux-gnu (default)\n"),
        )

        await expect(isRustupToolchainInstalled("stable")()).resolves.toEqual({
            success: true,
            value: true,
        })
    })

    it("returns false when no toolchain starts with the channel", async () => {
        runQuietly.mockResolvedValue(Result.ok("stable-x86_64-unknown-linux-gnu\n"))

        await expect(isRustupToolchainInstalled("nightly")()).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("returns false for an empty toolchain list", async () => {
        runQuietly.mockResolvedValue(Result.ok("no installed toolchains\n"))

        await expect(isRustupToolchainInstalled("stable")()).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("keeps the error of a list that failed", async () => {
        runQuietly.mockResolvedValue(Result.err(commandNotRun))

        await expect(isRustupToolchainInstalled("stable")()).resolves.toEqual({
            success: false,
            error: commandNotRun,
        })
    })
})

describe("isExecutableInPath", () => {
    const lookupCases: Array<{ platform: Platform; command: string }> = [
        { platform: "arch-linux", command: "which" },
        { platform: "mac-os", command: "which" },
        { platform: "windows", command: "where" },
    ]

    it.each(lookupCases)("uses $command on $platform", async ({ platform, command }) => {
        vi.resetModules()
        vi.doMock("../shared/platform", () => ({ platform }))
        vi.doMock("../process", () => ({ runQuietly, commandSucceeds }))
        const verification = await import("./verification")
        commandSucceeds.mockResolvedValue(Result.ok(true))

        await verification.isExecutableInPath("git")()

        expect(commandSucceeds).toHaveBeenCalledExactlyOnceWith(command, ["git"])
        vi.doUnmock("../shared/platform")
        vi.doUnmock("../process")
    })

    it("returns the answer of the lookup command", async () => {
        commandSucceeds.mockResolvedValue(Result.ok(false))

        await expect(isExecutableInPath("missing")()).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("does not run the lookup before the call", () => {
        isExecutableInPath("git")

        expect(commandSucceeds).not.toHaveBeenCalled()
    })

    it("keeps the error of a lookup that did not start", async () => {
        commandSucceeds.mockResolvedValue(Result.err(commandNotRun))

        await expect(isExecutableInPath("git")()).resolves.toEqual({
            success: false,
            error: commandNotRun,
        })
    })
})
