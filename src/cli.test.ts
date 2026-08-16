import { beforeEach, describe, expect, it, vi } from "vitest"

const exit = vi.hoisted(() => vi.fn())

vi.mock("node:process", async importOriginal => ({
    ...(await importOriginal<typeof import("node:process")>()),
    exit,
}))

const { parseCliOptions } = await import("./cli")

const ANSI = /\[\d+m/gu

const argvOf = (...flags: string[]): string[] => ["/usr/bin/node", "dotfiles", ...flags]

const errored = (): string =>
    vi
        .mocked(console.error)
        .mock.calls.map(call => call.join(" "))
        .join("\n")
        .replaceAll(ANSI, "")

beforeEach(() => {
    exit.mockReset()
    vi.spyOn(console, "error").mockImplementation(() => undefined)
})

describe("parseCliOptions", () => {
    it("runs the installs and copies the config files by default", () => {
        expect(parseCliOptions(argvOf())).toEqual({ dryRun: false, configs: true })
    })

    it.each(["true", "1", "yes", "on"])("reads --dry-run %s as true", value => {
        expect(parseCliOptions(argvOf("--dry-run", value)).dryRun).toBe(true)
    })

    it.each(["false", "0", "no", "off"])("reads --dry-run %s as false", value => {
        expect(parseCliOptions(argvOf("--dry-run", value)).dryRun).toBe(false)
    })

    it("reads --configs false", () => {
        expect(parseCliOptions(argvOf("--configs", "false")).configs).toBe(false)
    })

    it("reads both flags together", () => {
        expect(
            parseCliOptions(argvOf("--dry-run", "true", "--configs", "false")),
        ).toEqual({ dryRun: true, configs: false })
    })

    it("takes the last value of a flag that repeats", () => {
        expect(
            parseCliOptions(argvOf("--dry-run", "true", "--dry-run", "false")).dryRun,
        ).toBe(false)
    })

    it("ends the process when a flag takes a value that is not a boolean", () => {
        parseCliOptions(argvOf("--dry-run", "maybe"))

        expect(exit).toHaveBeenCalledExactlyOnceWith(1)
    })

    it("names the flag that carries the wrong value", () => {
        parseCliOptions(argvOf("--dry-run", "maybe"))

        expect(errored()).toContain("The flag --dry-run takes true or false")
    })

    it("names the configs flag in kebab case", () => {
        parseCliOptions(argvOf("--configs", "maybe"))

        expect(errored()).toContain("The flag --configs takes true or false")
    })

    it("names every flag that carries a wrong value", () => {
        parseCliOptions(argvOf("--dry-run", "maybe", "--configs", "perhaps"))
        const output = errored()

        expect(output).toContain("The flag --dry-run takes true or false")
        expect(output).toContain("The flag --configs takes true or false")
    })
})
