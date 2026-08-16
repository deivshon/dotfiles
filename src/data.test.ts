import { existsSync } from "node:fs"
import path from "node:path"

import { beforeEach, describe, expect, it, vi } from "vitest"

import { repositoryRoot } from "./configs/plan"
import { installableKey } from "./installables/installables"
import { Result } from "./shared/result"
import type { Configs } from "./types/configs"
import type { InstallableEntity, InstancedEntity } from "./types/entities"
import type { Installable } from "./types/installables"
import type { Instance } from "./types/instances"
import type { Platform } from "./types/platforms"

const runQuietly = vi.hoisted(() => vi.fn())
const commandSucceeds = vi.hoisted(() => vi.fn())

vi.mock("./process", () => ({ runQuietly, commandSucceeds, runInteractively: vi.fn() }))

const {
    applications,
    extensions,
    libraries,
    systemApplications,
    toolchains,
    userApplications,
} = await import("./data")
const { buildInstallPlan } = await import("./installs/plan")
const { nodesOfStep } = await import("./report")

const PLATFORMS: Platform[] = ["arch-linux", "mac-os", "windows"]

const entityOf = (installable: Installable): InstallableEntity | undefined => {
    const [kind, id] = installable
    if (kind === "application") {
        return applications[id]
    }
    if (kind === "library") {
        return libraries[id]
    }
    if (kind === "toolchain") {
        return toolchains[id]
    }
    return extensions[id]
}

const coversPlatform = (entity: InstallableEntity, platform: Platform): boolean =>
    "instances" in entity
        ? entity.instances[platform] !== null
        : entity.platform === platform

interface InstancedEntry {
    installable: Installable
    entity: InstancedEntity
}

const instancedEntities = (): InstancedEntry[] => [
    ...Object.values(userApplications).map((entity): InstancedEntry => ({
        installable: ["application", entity.id],
        entity,
    })),
    ...Object.values(libraries).map((entity): InstancedEntry => ({
        installable: ["library", entity.id],
        entity,
    })),
    ...Object.values(toolchains).map((entity): InstancedEntry => ({
        installable: ["toolchain", entity.id],
        entity,
    })),
    ...Object.values(extensions).map((entity): InstancedEntry => ({
        installable: ["extension", entity.id],
        entity,
    })),
]

/**
 * @param platform Target operating system
 * @description Returns every instance of the platform, with the installable that holds it.
 */
const instancesOfPlatform = (
    platform: Platform,
): Array<{ installable: Installable; instance: Instance }> =>
    instancedEntities().flatMap(({ installable, entity }) => {
        const instance = entity.instances[platform]
        return instance === null ? [] : [{ installable, instance }]
    })

/** @description Returns every dependency of every instance, with the platform that holds it. */
const everyDependency = (): Array<{
    installable: Installable
    required: Installable
    platform: Platform
}> =>
    PLATFORMS.flatMap(platform =>
        instancesOfPlatform(platform).flatMap(({ installable, instance }) =>
            instance.install.requires.map(required => ({
                installable,
                required,
                platform,
            })),
        ),
    )

const configsOfPlatform = (configs: Configs, platform: Platform) =>
    Array.isArray(configs) ? configs : configs[platform]

/**
 * @param platform Target operating system
 * @description Returns the plan of the platform, and throws when the plan does not build.
 */
const planOf = async (platform: Platform) => {
    const plan = await buildInstallPlan(platform)
    if (!plan.success) {
        throw new Error(plan.error.message)
    }
    return plan.value
}

beforeEach(() => {
    runQuietly.mockReset()
    commandSucceeds.mockReset()
    runQuietly.mockResolvedValue(Result.ok(""))
    commandSucceeds.mockResolvedValue(Result.ok(true))
})

describe("the shape of the catalog", () => {
    it.each([
        { name: "systemApplications", record: systemApplications },
        { name: "userApplications", record: userApplications },
        { name: "applications", record: applications },
        { name: "libraries", record: libraries },
        { name: "toolchains", record: toolchains },
        { name: "extensions", record: extensions },
    ])("gives every entry of $name the identifier of its key", ({ record }) => {
        for (const [key, entity] of Object.entries(record)) {
            expect(entity.id).toBe(key)
        }
    })

    it("holds every application of the two records in the joined record", () => {
        expect(Object.keys(applications).toSorted()).toEqual(
            [
                ...Object.keys(systemApplications),
                ...Object.keys(userApplications),
            ].toSorted(),
        )
    })

    it("points every entry of the joined record at its own entity", () => {
        for (const [id, application] of Object.entries(applications)) {
            const source =
                id in systemApplications ? systemApplications : userApplications
            expect(application).toBe(Reflect.get(source, id))
        }
    })

    it("gives every entity the kind of its record", () => {
        for (const application of Object.values(applications)) {
            expect(application.kind).toBe("application")
        }
        for (const entity of Object.values(libraries)) {
            expect(entity.kind).toBe("library")
        }
        for (const entity of Object.values(toolchains)) {
            expect(entity.kind).toBe("toolchain")
        }
        for (const entity of Object.values(extensions)) {
            expect(entity.kind).toBe("extension")
        }
    })

    it("gives every entity an install on one platform at least", () => {
        const orphans = instancedEntities()
            .filter(
                ({ entity }) =>
                    !PLATFORMS.some(platform => coversPlatform(entity, platform)),
            )
            .map(({ installable }) => installableKey(installable))

        expect(orphans).toEqual([])
    })

    it("gives every instance the platform of its slot", () => {
        for (const platform of PLATFORMS) {
            for (const { instance } of instancesOfPlatform(platform)) {
                expect(instance.platform).toBe(platform)
            }
        }
    })

    it("gives every system application the platform of its instance", () => {
        for (const application of Object.values(systemApplications)) {
            expect(application.instance.platform).toBe(application.platform)
        }
    })
})

describe("the dependencies of the catalog", () => {
    it("points every requires at an entity of the catalog", () => {
        const dangling = everyDependency()
            .filter(({ required }) => entityOf(required) === undefined)
            .map(
                ({ installable, required }) =>
                    `${installableKey(installable)} needs ${installableKey(required)}`,
            )

        expect(dangling).toEqual([])
    })

    it("gives every dependency an install on the platform that needs it", () => {
        const uncovered = everyDependency()
            .filter(({ required, platform }) => {
                const dependency = entityOf(required)
                return dependency === undefined || !coversPlatform(dependency, platform)
            })
            .map(
                ({ installable, required, platform }) =>
                    `on ${platform}, ${installableKey(installable)} needs ${installableKey(
                        required,
                    )}`,
            )

        expect(uncovered).toEqual([])
    })

    it("names the package manager of every package install in its requires", () => {
        const managers: Record<string, string> = {
            pacman: "application:pacman",
            paru: "application:paru",
            brew: "application:brew",
            winget: "application:winget",
        }

        for (const platform of PLATFORMS) {
            for (const { instance } of instancesOfPlatform(platform)) {
                if (instance.install.type === "package") {
                    expect(instance.install.requires.map(installableKey)).toEqual([
                        managers[instance.install.manager],
                    ])
                }
            }
        }
    })

    it("gives no installable a dependency on itself", () => {
        const selfReferences = everyDependency()
            .filter(
                ({ installable, required }) =>
                    installableKey(installable) === installableKey(required),
            )
            .map(({ installable }) => installableKey(installable))

        expect(selfReferences).toEqual([])
    })
})

describe("the plan of the catalog", () => {
    it.each(PLATFORMS)("builds a plan for %s", async platform => {
        await expect(buildInstallPlan(platform)).resolves.toMatchObject({
            success: true,
        })
    })

    it.each(PLATFORMS)("puts every installable of %s in the plan", async platform => {
        const plan = await planOf(platform)
        const planned = new Set(
            plan.steps.flatMap(step =>
                nodesOfStep(step).map(node => installableKey(node.installable)),
            ),
        )
        const roots = instancesOfPlatform(platform).map(({ installable }) =>
            installableKey(installable),
        )

        expect(roots.filter(key => !planned.has(key))).toEqual([])
    })

    it.each(PLATFORMS)("installs every installable of %s once", async platform => {
        const plan = await planOf(platform)
        const planned = plan.steps.flatMap(step =>
            nodesOfStep(step).map(node => installableKey(node.installable)),
        )

        expect(planned).toEqual([...new Set(planned)])
    })

    it.each(PLATFORMS)(
        "installs every dependency of %s in an earlier step",
        async platform => {
            const plan = await planOf(platform)
            const stepOf = new Map(
                plan.steps.flatMap((step, index) =>
                    nodesOfStep(step).map((node): [string, number] => [
                        installableKey(node.installable),
                        index,
                    ]),
                ),
            )

            const late = plan.steps.flatMap((step, index) =>
                nodesOfStep(step).flatMap(node =>
                    node.requires
                        .filter(required => {
                            const dependencyStep = stepOf.get(installableKey(required))
                            return dependencyStep !== undefined && dependencyStep >= index
                        })
                        .map(
                            required =>
                                `${installableKey(node.installable)} installs before ${installableKey(
                                    required,
                                )}`,
                        ),
                ),
            )

            expect(late).toEqual([])
        },
    )

    it.each(PLATFORMS)(
        "leaves every system application of %s out of the steps",
        async platform => {
            const plan = await planOf(platform)
            const planned = new Set(
                plan.steps.flatMap(step =>
                    nodesOfStep(step).map(node => installableKey(node.installable)),
                ),
            )

            for (const node of plan.systemApplications) {
                expect(planned.has(installableKey(node.installable))).toBe(false)
            }
        },
    )
})

describe("the config files of the catalog", () => {
    const everyConfig = (): Array<{
        id: string
        platform: Platform
        source: string[]
        destination: string[]
        type: string
    }> =>
        Object.values(applications).flatMap(application =>
            PLATFORMS.flatMap(platform =>
                configsOfPlatform(application.configs, platform).map(config => ({
                    id: application.id,
                    platform,
                    source: config.source,
                    destination: config.destination,
                    type: config.type,
                })),
            ),
        )

    it("points every source at a file of the repository", () => {
        const missing = everyConfig()
            .filter(config => !existsSync(path.resolve(repositoryRoot, ...config.source)))
            .map(config => `${config.id}: ${config.source.join("/")}`)

        expect([...new Set(missing)]).toEqual([])
    })

    it("keeps every source inside the repository", () => {
        const outside = everyConfig()
            .filter(
                config =>
                    !path
                        .resolve(repositoryRoot, ...config.source)
                        .startsWith(`${repositoryRoot}${path.sep}`),
            )
            .map(config => `${config.id}: ${config.source.join("/")}`)

        expect([...new Set(outside)]).toEqual([])
    })

    it("holds a JSON file at both ends of every merge", () => {
        for (const config of everyConfig()) {
            if (config.type === "json-merge") {
                expect(config.source.at(-1)).toMatch(/\.jsonc?$/u)
                expect(config.destination.at(-1)).toMatch(/\.jsonc?$/u)
            }
        }
    })

    it("gives no application two config files with the same destination", () => {
        for (const application of Object.values(applications)) {
            for (const platform of PLATFORMS) {
                const destinations = configsOfPlatform(application.configs, platform).map(
                    config => config.destination.join("/"),
                )
                expect(destinations).toEqual([...new Set(destinations)])
            }
        }
    })
})
