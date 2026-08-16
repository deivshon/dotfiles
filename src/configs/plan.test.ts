import { existsSync } from "node:fs"
import { homedir } from "node:os"
import path from "node:path"

import { beforeEach, describe, expect, it, vi } from "vitest"

import { installableKey } from "../installables/installables"
import type { ConfigTarget } from "../types/configs"
import type { Instances } from "../types/instances"
import type { Platform } from "../types/platforms"

const isConfigCurrent = vi.hoisted(() => vi.fn())
const fixtures = vi.hoisted(() => ({ applications: {} }))

vi.mock("./configs", () => ({ isConfigCurrent }))
vi.mock("../data", () => fixtures)

const {
    archLinuxSystemApplication,
    brewFormula,
    fileCopy,
    jsonMerge,
    macOsSystemApplication,
    pacmanPackage,
    userApplication,
} = await import("../installables/builders")
const { buildConfigPlan, repositoryRoot } = await import("./plan")

const PLATFORMS: Platform[] = ["arch-linux", "mac-os", "windows"]

const noInstances: Instances = {
    "arch-linux": null,
    "mac-os": null,
    windows: null,
}

const archAndMac: Instances = {
    "arch-linux": pacmanPackage("any-package"),
    "mac-os": brewFormula("any-package"),
    windows: null,
}

const archOnly: Instances = { ...noInstances, "arch-linux": pacmanPackage("any") }

/**
 * @param applications Applications that the plan reads
 * @param platform Target operating system
 * @description Replaces the applications of the plan, and returns the plan of the platform.
 */
const planOf = (applications: object, platform: Platform = "arch-linux") => {
    for (const key of Object.keys(fixtures.applications)) {
        Reflect.deleteProperty(fixtures.applications, key)
    }
    Object.assign(fixtures.applications, applications)

    return buildConfigPlan(platform)
}

const destinationsOf = (targets: ConfigTarget[], id: string): string[] =>
    targets
        .filter(target => installableKey(target.installable) === `application:${id}`)
        .map(target => target.destination)

beforeEach(() => {
    isConfigCurrent.mockReset()
    isConfigCurrent.mockResolvedValue(false)
})

describe("repositoryRoot", () => {
    it("points at the directory that holds the files directory", () => {
        expect(existsSync(path.join(repositoryRoot, "files"))).toBe(true)
    })

    it("is an absolute path", () => {
        expect(path.isAbsolute(repositoryRoot)).toBe(true)
    })
})

describe("buildConfigPlan paths", () => {
    it("resolves the source against the root of the repository", async () => {
        const targets = await planOf({
            ghostty: userApplication("ghostty", archOnly, [
                fileCopy(["files", "ghostty", "config"], ["~", ".config", "ghostty"]),
            ]),
        })

        expect(targets[0]?.source).toBe(
            path.join(repositoryRoot, "files", "ghostty", "config"),
        )
    })

    it("replaces the home prefix with the home directory", async () => {
        const targets = await planOf({
            ghostty: userApplication("ghostty", archOnly, [
                fileCopy(["files", "a"], ["~", ".config", "app", "config.toml"]),
            ]),
        })

        expect(targets[0]?.destination).toBe(
            path.join(homedir(), ".config", "app", "config.toml"),
        )
    })

    it("keeps a destination that does not start at the home directory", async () => {
        const targets = await planOf({
            ghostty: userApplication("ghostty", archOnly, [
                fileCopy(["files", "a"], ["/etc", "app", "config.toml"]),
            ]),
        })

        expect(targets[0]?.destination).toBe(path.join("/etc", "app", "config.toml"))
    })

    it("resolves a destination of one segment", async () => {
        const targets = await planOf({
            ghostty: userApplication("ghostty", archOnly, [
                fileCopy(["files", "a"], ["~"]),
            ]),
        })

        expect(targets[0]?.destination).toBe(homedir())
    })

    it("keeps the type of every config file", async () => {
        const targets = await planOf({
            ghostty: userApplication("ghostty", archOnly, [
                fileCopy(["files", "a"], ["~", "a"]),
                jsonMerge(["files", "b.json"], ["~", "b.json"]),
            ]),
        })

        expect(targets.map(target => target.type)).toEqual(["file-copy", "json-merge"])
    })
})

describe("buildConfigPlan platform selection", () => {
    it("gives the config files of a flat list to every platform of the application", async () => {
        const configs = [fileCopy(["files", "a"], ["~", ".config", "a"])]
        const destination = path.join(homedir(), ".config", "a")

        expect(
            destinationsOf(
                await planOf(
                    { ghostty: userApplication("ghostty", archAndMac, configs) },
                    "arch-linux",
                ),
                "ghostty",
            ),
        ).toEqual([destination])
        expect(
            destinationsOf(
                await planOf(
                    { ghostty: userApplication("ghostty", archAndMac, configs) },
                    "mac-os",
                ),
                "ghostty",
            ),
        ).toEqual([destination])
    })

    it("picks the list of the platform from a config record", async () => {
        const application = () =>
            userApplication("visual-studio-code", archAndMac, {
                "arch-linux": [jsonMerge(["files", "s.json"], ["~", "arch.json"])],
                "mac-os": [jsonMerge(["files", "s.json"], ["~", "mac.json"])],
                windows: [],
            })

        expect(
            destinationsOf(
                await planOf({ "visual-studio-code": application() }, "arch-linux"),
                "visual-studio-code",
            ),
        ).toEqual([path.join(homedir(), "arch.json")])
        expect(
            destinationsOf(
                await planOf({ "visual-studio-code": application() }, "mac-os"),
                "visual-studio-code",
            ),
        ).toEqual([path.join(homedir(), "mac.json")])
    })

    it("gives no target for a platform whose list in the record is empty", async () => {
        const targets = await planOf(
            {
                "visual-studio-code": userApplication("visual-studio-code", archAndMac, {
                    "arch-linux": [jsonMerge(["files", "s.json"], ["~", "a.json"])],
                    "mac-os": [],
                    windows: [],
                }),
            },
            "mac-os",
        )

        expect(targets).toEqual([])
    })

    it("leaves out an application with no instance on the platform", async () => {
        const targets = await planOf(
            {
                ghostty: userApplication("ghostty", archOnly, [
                    fileCopy(["files", "a"], ["~", "a"]),
                ]),
            },
            "mac-os",
        )

        expect(targets).toEqual([])
    })

    it("keeps a system application on its own platform", async () => {
        const targets = await planOf(
            {
                pacman: archLinuxSystemApplication("pacman", [
                    fileCopy(["files", "pacman.conf"], ["/etc", "pacman.conf"]),
                ]),
            },
            "arch-linux",
        )

        expect(targets.map(target => target.destination)).toEqual([
            path.join("/etc", "pacman.conf"),
        ])
    })

    it("leaves out a system application of another platform", async () => {
        const targets = await planOf(
            {
                curl: macOsSystemApplication("curl", [
                    fileCopy(["files", "curlrc"], ["~", ".curlrc"]),
                ]),
            },
            "arch-linux",
        )

        expect(targets).toEqual([])
    })

    it("gives an application with no config file no target", async () => {
        const targets = await planOf({
            git: userApplication("git", archOnly),
        })

        expect(targets).toEqual([])
    })

    it("returns an empty plan for an empty catalog", async () => {
        expect(await planOf({})).toEqual([])
    })
})

describe("buildConfigPlan targets", () => {
    const twoApplications = () => ({
        ghostty: userApplication("ghostty", archOnly, [
            fileCopy(["files", "a"], ["~", "a"]),
            fileCopy(["files", "b"], ["~", "b"]),
        ]),
        git: userApplication("git", archOnly, [
            jsonMerge(["files", "c.json"], ["~", "c.json"]),
        ]),
    })

    it("keeps every config file of every application", async () => {
        const targets = await planOf(twoApplications())

        expect(targets.map(target => target.destination)).toEqual([
            path.join(homedir(), "a"),
            path.join(homedir(), "b"),
            path.join(homedir(), "c.json"),
        ])
    })

    it("names the application of every config file", async () => {
        const targets = await planOf(twoApplications())

        expect(targets.map(target => installableKey(target.installable))).toEqual([
            "application:ghostty",
            "application:ghostty",
            "application:git",
        ])
    })

    it.each(PLATFORMS)(
        "resolves every destination to an absolute path on %s",
        async platform => {
            const targets = await planOf(
                {
                    ghostty: userApplication("ghostty", archAndMac, [
                        fileCopy(["files", "a"], ["~", "a"]),
                    ]),
                },
                platform,
            )

            for (const target of targets) {
                expect(path.isAbsolute(target.destination)).toBe(true)
            }
        },
    )
})

describe("buildConfigPlan skip flag", () => {
    const application = () => ({
        ghostty: userApplication("ghostty", archOnly, [
            fileCopy(["files", "a"], ["~", "a"]),
            jsonMerge(["files", "b.json"], ["~", "b.json"]),
        ]),
    })

    it("reads the state of every destination once", async () => {
        const targets = await planOf(application())

        expect(isConfigCurrent).toHaveBeenCalledTimes(targets.length)
    })

    it("asks about the type, the source, and the destination alone", async () => {
        await planOf(application())

        for (const [argument] of isConfigCurrent.mock.calls) {
            expect(Object.keys(argument).toSorted()).toEqual([
                "destination",
                "source",
                "type",
            ])
        }
    })

    it("marks a target that the destination holds already", async () => {
        isConfigCurrent.mockResolvedValue(true)

        const targets = await planOf(application())

        expect(targets.map(target => target.skip)).toEqual([true, true])
    })

    it("marks a target that the destination does not hold", async () => {
        const targets = await planOf(application())

        expect(targets.map(target => target.skip)).toEqual([false, false])
    })

    it("marks each target on its own", async () => {
        isConfigCurrent.mockImplementation(
            async (target: { type: string }) => target.type === "json-merge",
        )

        const targets = await planOf(application())

        expect(targets.map(target => target.skip)).toEqual([false, true])
    })
})
