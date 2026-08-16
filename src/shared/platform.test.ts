import { afterEach, describe, expect, it, vi } from "vitest"

import type { Platform } from "../types/platforms"

/**
 * @param operatingSystem Value that `node:process` reports
 * @description Returns the platform that the module reads for the operating system.
 */
const platformOf = async (operatingSystem: string) => {
    const exit = vi.fn()
    vi.resetModules()
    vi.doMock("node:process", async importOriginal => ({
        ...(await importOriginal<typeof import("node:process")>()),
        platform: operatingSystem,
        exit,
    }))

    const { platform } = await import("./platform")
    return { platform, exit }
}

afterEach(() => {
    vi.doUnmock("node:process")
    vi.resetModules()
})

describe("platform", () => {
    it.each([
        { operatingSystem: "linux", expected: "arch-linux" satisfies Platform },
        { operatingSystem: "darwin", expected: "mac-os" satisfies Platform },
        { operatingSystem: "win32", expected: "windows" satisfies Platform },
    ])("reads $operatingSystem as $expected", async ({ operatingSystem, expected }) => {
        const { platform, exit } = await platformOf(operatingSystem)

        expect(platform).toBe(expected)
        expect(exit).not.toHaveBeenCalled()
    })

    it.each(["freebsd", "aix", "sunos", "android"])(
        "ends the process on %s",
        async operatingSystem => {
            vi.spyOn(console, "error").mockImplementation(() => undefined)

            const { exit } = await platformOf(operatingSystem)

            expect(exit).toHaveBeenCalledExactlyOnceWith(1)
        },
    )

    it("names the operating system that it does not support", async () => {
        const error = vi.spyOn(console, "error").mockImplementation(() => undefined)

        await platformOf("freebsd")

        expect(error.mock.calls.map(call => call.join(" ")).join("\n")).toContain(
            "Unsupported operating system: freebsd",
        )
    })
})
