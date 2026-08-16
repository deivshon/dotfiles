import { beforeEach, describe, expect, it, vi } from "vitest"

import { installableKey } from "../installables/installables"
import { Result } from "../shared/result"
import type { Installable } from "../types/installables"
import type { Instances } from "../types/instances"
import type { Platform } from "../types/platforms"
import type { InstallStep } from "./plan"

const runQuietly = vi.hoisted(() => vi.fn())
const commandSucceeds = vi.hoisted(() => vi.fn())

vi.mock("../process", () => ({ runQuietly, commandSucceeds, runInteractively: vi.fn() }))

const {
    archLinuxCustomInstall,
    archLinuxSystemApplication,
    brewCask,
    brewFormula,
    extension,
    library,
    macOsCustomInstall,
    macOsSystemApplication,
    pacmanPackage,
    paruPackage,
    toolchain,
    userApplication,
    windowsSystemApplication,
} = await import("../installables/builders")

const noInstances: Instances = {
    "arch-linux": null,
    "mac-os": null,
    windows: null,
}

const custom = (requires: Installable[]) =>
    archLinuxCustomInstall({
        install: () => Promise.resolve(Result.ok(undefined)),
        isInstalled: () => Promise.resolve(Result.ok(false)),
        requires,
    })

const macCustom = (requires: Installable[]) =>
    macOsCustomInstall({
        install: () => Promise.resolve(Result.ok(undefined)),
        isInstalled: () => Promise.resolve(Result.ok(false)),
        requires,
    })

/** @remarks Every package install requires its package manager, so the lookup must hold one. */
const packageManagers = {
    pacman: archLinuxSystemApplication("pacman"),
    makepkg: archLinuxSystemApplication("makepkg"),
    curl: macOsSystemApplication("curl"),
    winget: windowsSystemApplication("winget"),
    paru: userApplication("paru", { ...noInstances, "arch-linux": custom([]) }),
    brew: userApplication("brew", { ...noInstances, "mac-os": macCustom([]) }),
}

const fixtures = vi.hoisted(() => ({
    applications: {},
    userApplications: {},
    libraries: {},
    toolchains: {},
    extensions: {},
}))

vi.mock("../data", () => fixtures)

const { buildInstallPlan } = await import("./plan")

const refill = (record: object, values: object): void => {
    for (const key of Object.keys(record)) {
        Reflect.deleteProperty(record, key)
    }
    Object.assign(record, values)
}

/**
 * @param data Entities that the plan reads
 * @param platform Target operating system
 * @description Replaces the entities of the plan, and returns the plan of the platform.
 */
const planOf = (
    data: {
        userApplications?: object
        systemApplications?: object
        libraries?: object
        toolchains?: object
        extensions?: object
    },
    platform: Platform = "arch-linux",
) => {
    const userApplications = data.userApplications ?? {}
    const systemApplications = data.systemApplications ?? {}
    refill(fixtures.userApplications, userApplications)
    refill(fixtures.libraries, data.libraries ?? {})
    refill(fixtures.toolchains, data.toolchains ?? {})
    refill(fixtures.extensions, data.extensions ?? {})
    refill(fixtures.applications, {
        ...packageManagers,
        ...systemApplications,
        ...userApplications,
    })

    return buildInstallPlan(platform)
}

const keysOfPlan = (steps: InstallStep[]): string[][] =>
    steps.map(step =>
        (step.type === "custom" ? [step.node] : step.nodes).map(node =>
            installableKey(node.installable),
        ),
    )

beforeEach(() => {
    runQuietly.mockReset()
    commandSucceeds.mockReset()
    runQuietly.mockResolvedValue(Result.ok(""))
    commandSucceeds.mockResolvedValue(Result.ok(false))
})

describe("buildInstallPlan channels", () => {
    it("maps a pacman package to the standard Arch Linux channel", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.steps).toMatchObject([
            {
                type: "package",
                channel: "arch-standard",
                nodes: [{ packageName: "git", skip: false }],
            },
        ])
    })

    it("maps a paru package to the AUR channel", async () => {
        const plan = await planOf({
            userApplications: {
                bat: userApplication("bat", {
                    ...noInstances,
                    "arch-linux": paruPackage("bat-bin"),
                }),
            },
        })

        expect(plan.success && plan.value.steps.at(-1)).toMatchObject({
            channel: "arch-aur",
            nodes: [{ packageName: "bat-bin" }],
        })
    })

    it("installs paru before the AUR packages that need it", async () => {
        const plan = await planOf({
            userApplications: {
                bat: userApplication("bat", {
                    ...noInstances,
                    "arch-linux": paruPackage("bat-bin"),
                }),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:paru"],
            ["application:bat"],
        ])
    })

    it("maps a Homebrew formula to the formula channel", async () => {
        const plan = await planOf(
            {
                userApplications: {
                    eza: userApplication("eza", {
                        ...noInstances,
                        "mac-os": brewFormula("eza"),
                    }),
                },
            },
            "mac-os",
        )

        expect(plan.success && plan.value.steps.at(-1)).toMatchObject({
            channel: "brew-formula",
            nodes: [{ packageName: "eza" }],
        })
    })

    it("maps a Homebrew cask to the cask channel", async () => {
        const plan = await planOf(
            {
                userApplications: {
                    firefox: userApplication("firefox", {
                        ...noInstances,
                        "mac-os": brewCask("firefox"),
                    }),
                },
            },
            "mac-os",
        )

        expect(plan.success && plan.value.steps.at(-1)).toMatchObject({
            channel: "brew-cask",
            nodes: [{ packageName: "firefox" }],
        })
    })

    it("reports a winget package as an install that is not supported", async () => {
        const plan = await planOf(
            {
                userApplications: {
                    wget: userApplication("wget", {
                        ...noInstances,
                        windows: {
                            platform: "windows",
                            install: {
                                type: "package",
                                manager: "winget",
                                packageName: "wget",
                                requires: [["application", "winget"]],
                            },
                        },
                    }),
                },
            },
            "windows",
        )

        expect(plan).toEqual({
            success: false,
            error: {
                type: "unsupported-install",
                installable: ["application", "wget"],
                message:
                    'The winget install of the application "wget" is not supported yet',
            },
        })
    })
})

describe("buildInstallPlan verification", () => {
    it("marks a package that the package manager lists already", async () => {
        runQuietly.mockResolvedValue(Result.ok("git\n"))

        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.steps).toMatchObject([
            { nodes: [{ skip: true }] },
        ])
    })

    it("reads the AUR list for an AUR package and the standard list for a standard one", async () => {
        runQuietly.mockResolvedValue(Result.ok(""))

        await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
                bat: userApplication("bat", {
                    ...noInstances,
                    "arch-linux": paruPackage("bat-bin"),
                }),
            },
        })

        expect(runQuietly.mock.calls).toEqual(
            expect.arrayContaining([
                ["pacman", ["-Qnq"]],
                ["pacman", ["-Qmq"]],
            ]),
        )
    })

    it("returns the error of a verification that did not run", async () => {
        const error = {
            type: "command-not-run" as const,
            command: "pacman -Qnq",
            cause: new Error("ENOENT"),
            message: "The command did not start",
        }
        runQuietly.mockResolvedValue(Result.err(error))

        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan).toEqual({ success: false, error })
    })

    it("marks a custom install that its own check finds", async () => {
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": archLinuxCustomInstall({
                        install: () => Promise.resolve(Result.ok(undefined)),
                        isInstalled: () => Promise.resolve(Result.ok(true)),
                        requires: [],
                    }),
                }),
            },
        })

        expect(plan.success && plan.value.steps).toMatchObject([
            { type: "custom", node: { skip: true } },
        ])
    })
})

describe("buildInstallPlan system applications", () => {
    it("keeps a system application out of the steps", async () => {
        commandSucceeds.mockResolvedValue(Result.ok(true))

        const plan = await planOf({
            systemApplications: { pacman: archLinuxSystemApplication("pacman") },
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.systemApplications).toMatchObject([
            { type: "system", installable: ["application", "pacman"], skip: true },
        ])
        expect(plan.success && plan.value.steps).toHaveLength(1)
    })

    it("marks a system application that the machine does not provide", async () => {
        commandSucceeds.mockResolvedValue(Result.ok(false))

        const plan = await planOf({
            systemApplications: { pacman: archLinuxSystemApplication("pacman") },
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.systemApplications).toMatchObject([
            { skip: false },
        ])
    })

    it("gives a system application no dependency", async () => {
        commandSucceeds.mockResolvedValue(Result.ok(true))

        const plan = await planOf({
            systemApplications: { pacman: archLinuxSystemApplication("pacman") },
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.systemApplications[0]?.requires).toEqual([])
    })

    it("sorts the system applications by their key", async () => {
        commandSucceeds.mockResolvedValue(Result.ok(true))

        const plan = await planOf({
            systemApplications: {
                pacman: archLinuxSystemApplication("pacman"),
                makepkg: archLinuxSystemApplication("makepkg"),
            },
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": custom([
                        ["application", "pacman"],
                        ["application", "makepkg"],
                    ]),
                }),
            },
        })

        expect(
            plan.success &&
                plan.value.systemApplications.map(node => node.installable[1]),
        ).toEqual(["makepkg", "pacman"])
    })

    it("reports a system application of another platform as unavailable", async () => {
        const plan = await planOf({
            systemApplications: { winget: windowsSystemApplication("winget") },
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": custom([["application", "winget"]]),
                }),
            },
        })

        expect(plan).toEqual({
            success: false,
            error: {
                type: "installable-unavailable",
                installable: ["application", "winget"],
                platform: "arch-linux",
                message: 'The application "winget" has no install for arch-linux',
            },
        })
    })
})

describe("buildInstallPlan dependencies", () => {
    it("pulls a dependency that is not a root into the plan", async () => {
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([["library", "base-devel"]]),
                }),
            },
            libraries: {
                "base-devel": library("base-devel", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("base-devel"),
                }),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["library:base-devel"],
            ["application:ccommit"],
        ])
    })

    it("installs a dependency of a dependency first", async () => {
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([["toolchain", "rust-stable"]]),
                }),
                rustup: userApplication("rustup", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("rustup"),
                }),
            },
            toolchains: {
                "rust-stable": toolchain("rust-stable", {
                    ...noInstances,
                    "arch-linux": custom([["application", "rustup"]]),
                }),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:rustup"],
            ["toolchain:rust-stable"],
            ["application:ccommit"],
        ])
    })

    it("resolves a shared dependency once", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([["application", "git"]]),
                }),
                paru: userApplication("paru", {
                    ...noInstances,
                    "arch-linux": custom([["application", "git"]]),
                }),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:git"],
            ["application:ccommit"],
            ["application:paru"],
        ])
    })

    it("reports a dependency that the platform does not cover", async () => {
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([["application", "brew"]]),
                }),
                brew: userApplication("brew", noInstances),
            },
        })

        expect(plan).toEqual({
            success: false,
            error: {
                type: "installable-unavailable",
                installable: ["application", "brew"],
                platform: "arch-linux",
                message: 'The application "brew" has no install for arch-linux',
            },
        })
    })

    it("reports a cycle of two installables", async () => {
        const plan = await planOf({
            userApplications: {
                dash: userApplication("dash", {
                    ...noInstances,
                    "arch-linux": custom([["application", "doas"]]),
                }),
                doas: userApplication("doas", {
                    ...noInstances,
                    "arch-linux": custom([["application", "dash"]]),
                }),
            },
        })

        expect(plan.success).toBe(false)
        expect(!plan.success && plan.error.type).toBe("dependency-cycle")
        expect(!plan.success && plan.error.message).toBe(
            'The dependencies form a cycle: application "dash" -> application "doas" -> application "dash"',
        )
    })

    it("reports an installable that requires itself", async () => {
        const plan = await planOf({
            userApplications: {
                dash: userApplication("dash", {
                    ...noInstances,
                    "arch-linux": custom([["application", "dash"]]),
                }),
            },
        })

        expect(!plan.success && plan.error.type).toBe("dependency-cycle")
    })
})

describe("buildInstallPlan steps", () => {
    it("groups the packages of one channel and one level into one step", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
                bat: userApplication("bat", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("bat"),
                }),
            },
        })

        expect(plan.success && plan.value.steps).toHaveLength(1)
        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:git", "application:bat"],
        ])
    })

    it("gives every channel of one level its own step", async () => {
        const plan = await planOf(
            {
                userApplications: {
                    eza: userApplication("eza", {
                        ...noInstances,
                        "mac-os": brewFormula("eza"),
                    }),
                    firefox: userApplication("firefox", {
                        ...noInstances,
                        "mac-os": brewCask("firefox"),
                    }),
                },
            },
            "mac-os",
        )

        expect(
            plan.success &&
                plan.value.steps.map(step =>
                    step.type === "package" ? step.channel : step.type,
                ),
        ).toEqual(["custom", "brew-formula", "brew-cask"])
    })

    it("gives every custom install its own step", async () => {
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([]),
                }),
                paru: userApplication("paru", {
                    ...noInstances,
                    "arch-linux": custom([]),
                }),
            },
        })

        expect(plan.success && plan.value.steps.map(step => step.type)).toEqual([
            "custom",
            "custom",
        ])
    })

    it("puts the custom installs of a level before its packages", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": custom([]),
                }),
            },
        })

        expect(plan.success && plan.value.steps.map(step => step.type)).toEqual([
            "custom",
            "package",
        ])
    })

    it("carries the install command of the channel", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })
        const step = plan.success ? plan.value.steps[0] : undefined

        expect(step?.type === "package" && typeof step.install).toBe("function")
    })

    it("carries the install command of a custom node", async () => {
        const install = vi.fn(() => Promise.resolve(Result.ok(undefined)))
        const plan = await planOf({
            userApplications: {
                ccommit: userApplication("ccommit", {
                    ...noInstances,
                    "arch-linux": archLinuxCustomInstall({
                        install,
                        isInstalled: () => Promise.resolve(Result.ok(false)),
                        requires: [],
                    }),
                }),
            },
        })
        const step = plan.success ? plan.value.steps[0] : undefined

        expect(step?.type === "custom" && step.node.install).toBe(install)
        expect(install).not.toHaveBeenCalled()
    })

    it("keeps a node that is present already in the plan", async () => {
        runQuietly.mockResolvedValue(Result.ok("git\n"))

        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
        })

        expect(plan.success && plan.value.steps).toHaveLength(1)
        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:git"],
        ])
    })

    it("returns an empty plan when the platform covers nothing", async () => {
        const plan = await planOf({})

        expect(plan).toEqual({
            success: true,
            value: { systemApplications: [], steps: [] },
        })
    })
})

describe("buildInstallPlan roots", () => {
    it("takes the roots of every kind", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
            },
            libraries: {
                "base-devel": library("base-devel", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("base-devel"),
                }),
            },
            toolchains: {
                "rust-stable": toolchain("rust-stable", {
                    ...noInstances,
                    "arch-linux": custom([]),
                }),
            },
            extensions: {
                "oxc-vscode": extension("oxc-vscode", {
                    ...noInstances,
                    "arch-linux": custom([]),
                }),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps).flat().toSorted()).toEqual([
            "application:git",
            "extension:oxc-vscode",
            "library:base-devel",
            "toolchain:rust-stable",
        ])
    })

    it("leaves out a root that the platform does not cover", async () => {
        const plan = await planOf({
            userApplications: {
                git: userApplication("git", {
                    ...noInstances,
                    "arch-linux": pacmanPackage("git"),
                }),
                brew: userApplication("brew", noInstances),
            },
        })

        expect(plan.success && keysOfPlan(plan.value.steps)).toEqual([
            ["application:git"],
        ])
    })
})
