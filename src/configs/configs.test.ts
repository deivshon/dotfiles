import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ConfigTarget, ConfigTargetBase } from "../types/configs"

vi.mock("node:fs", async () => {
    const { fs } = await import("memfs")
    return { ...fs, default: fs }
})
vi.mock("node:fs/promises", async () => {
    const { fs } = await import("memfs")
    return { ...fs.promises, default: fs.promises }
})

const { vol } = await import("memfs")
const { applyConfig, isConfigCurrent } = await import("./configs")

const SOURCE = "/repo/files/app/config.json"
const DESTINATION = "/home/user/.config/app/config.json"
const NOW = 1_700_000_000_000

const base = (type: ConfigTargetBase["type"] = "file-copy"): ConfigTargetBase => ({
    type,
    source: SOURCE,
    destination: DESTINATION,
})

const target = (type: ConfigTarget["type"] = "file-copy"): ConfigTarget => ({
    ...base(type),
    installable: ["application", "ghostty"],
    skip: false,
})

const write = (files: Record<string, string>): void => {
    vol.fromJSON(files)
}

beforeEach(() => {
    vol.reset()
    vi.spyOn(Date, "now").mockReturnValue(NOW)
})

describe("isConfigCurrent", () => {
    it("returns false when the destination is absent", async () => {
        write({ [SOURCE]: "content" })

        await expect(isConfigCurrent(base())).resolves.toBe(false)
    })

    it("returns true when a copy holds the content of the source", async () => {
        write({ [SOURCE]: "content", [DESTINATION]: "content" })

        await expect(isConfigCurrent(base())).resolves.toBe(true)
    })

    it("returns false when a copy holds another content", async () => {
        write({ [SOURCE]: "content", [DESTINATION]: "other" })

        await expect(isConfigCurrent(base())).resolves.toBe(false)
    })

    it("returns false when the source is absent", async () => {
        write({ [DESTINATION]: "content" })

        await expect(isConfigCurrent(base())).resolves.toBe(false)
    })

    it("returns true when a merge changes nothing", async () => {
        write({
            [SOURCE]: '{"a":1}',
            [DESTINATION]: '{\n    "a": 1,\n    "b": 2\n}',
        })

        await expect(isConfigCurrent(base("json-merge"))).resolves.toBe(true)
    })

    it("returns false when a merge changes a value", async () => {
        write({
            [SOURCE]: '{"a":9}',
            [DESTINATION]: '{\n    "a": 1\n}',
        })

        await expect(isConfigCurrent(base("json-merge"))).resolves.toBe(false)
    })

    it("returns false when a merge cannot read the destination", async () => {
        write({ [SOURCE]: '{"a":1}', [DESTINATION]: "not json" })

        await expect(isConfigCurrent(base("json-merge"))).resolves.toBe(false)
    })

    it("compares the bytes and not the text", async () => {
        write({ [SOURCE]: "content\n", [DESTINATION]: "content" })

        await expect(isConfigCurrent(base())).resolves.toBe(false)
    })

    it("writes nothing", async () => {
        write({ [SOURCE]: "content", [DESTINATION]: "other" })

        await isConfigCurrent(base())

        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("other")
    })
})

describe("applyConfig", () => {
    it("copies the source to an absent destination", async () => {
        write({ [SOURCE]: "content" })

        const result = await applyConfig(target())

        expect(result).toEqual({
            success: true,
            value: { target: target(), status: "copied", backupPath: null },
        })
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("content")
    })

    it("builds the directory of the destination", async () => {
        write({ [SOURCE]: "content" })

        await applyConfig(target())

        expect(vol.existsSync("/home/user/.config/app")).toBe(true)
    })

    it("reports a destination that holds the content already", async () => {
        write({ [SOURCE]: "content", [DESTINATION]: "content" })

        const result = await applyConfig(target())

        expect(result).toEqual({
            success: true,
            value: { target: target(), status: "unchanged", backupPath: null },
        })
    })

    it("renames a destination of another content before the write", async () => {
        write({ [SOURCE]: "new", [DESTINATION]: "old" })

        const result = await applyConfig(target())
        const backupPath = `${DESTINATION}.bkp-${NOW}`

        expect(result).toEqual({
            success: true,
            value: { target: target(), status: "replaced", backupPath },
        })
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("new")
        expect(vol.readFileSync(backupPath, "utf8")).toBe("old")
    })

    it("merges into a destination instead of replacing it", async () => {
        write({
            [SOURCE]: '{"a":9}',
            [DESTINATION]: '{\n    // keep me\n    "a": 1,\n    "b": 2\n}',
        })

        await applyConfig(target("json-merge"))

        expect(vol.readFileSync(DESTINATION, "utf8")).toBe(
            '{\n    // keep me\n    "a": 9,\n    "b": 2\n}',
        )
    })

    it("copies the source when a merge finds no destination", async () => {
        write({ [SOURCE]: '{"a":1}' })

        const result = await applyConfig(target("json-merge"))

        expect(result.success && result.value.status).toBe("copied")
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe('{"a":1}')
    })

    it("keeps a merge that changes nothing unchanged", async () => {
        write({ [SOURCE]: '{"a":1}', [DESTINATION]: '{\n    "a": 1\n}' })

        const result = await applyConfig(target("json-merge"))

        expect(result.success && result.value.status).toBe("unchanged")
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe('{\n    "a": 1\n}')
    })

    it("returns a file-system error when the source is absent", async () => {
        write({ [DESTINATION]: "old" })

        const result = await applyConfig(target())

        expect(result).toEqual({
            success: false,
            error: {
                type: "file-system-failed",
                path: SOURCE,
                cause: expect.anything(),
                message: `The config file "${SOURCE}" was not read`,
            },
        })
    })

    it("leaves the destination alone when the source is absent", async () => {
        write({ [DESTINATION]: "old" })

        await applyConfig(target())

        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("old")
        expect(vol.existsSync(`${DESTINATION}.bkp-${NOW}`)).toBe(false)
    })

    it("returns the error of a merge that cannot read the destination", async () => {
        write({ [SOURCE]: '{"a":1}', [DESTINATION]: "not json" })

        const result = await applyConfig(target("json-merge"))

        expect(result).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: DESTINATION,
                message: `The file "${DESTINATION}" is not valid JSON`,
            },
        })
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("not json")
    })

    it("returns a file-system error when the destination is not readable", async () => {
        write({ [SOURCE]: "content" })
        vol.mkdirSync(DESTINATION, { recursive: true })

        const result = await applyConfig(target())

        expect(result).toEqual({
            success: false,
            error: {
                type: "file-system-failed",
                path: DESTINATION,
                cause: expect.anything(),
                message: `The file "${DESTINATION}" was not read`,
            },
        })
    })

    it("returns a file-system error when the write fails", async () => {
        write({ [SOURCE]: "content", "/home/user/.config/app": "a file, not a folder" })

        const result = await applyConfig(target())

        expect(result).toEqual({
            success: false,
            error: {
                type: "file-system-failed",
                path: DESTINATION,
                cause: expect.anything(),
                message: `The config file "${SOURCE}" was not written to "${DESTINATION}"`,
            },
        })
    })

    it("keeps one backup per run", async () => {
        write({ [SOURCE]: "one", [DESTINATION]: "old" })
        await applyConfig(target())

        vol.writeFileSync(SOURCE, "two")
        vi.spyOn(Date, "now").mockReturnValue(NOW + 1)
        await applyConfig(target())

        expect(vol.readFileSync(`${DESTINATION}.bkp-${NOW}`, "utf8")).toBe("old")
        expect(vol.readFileSync(`${DESTINATION}.bkp-${NOW + 1}`, "utf8")).toBe("one")
        expect(vol.readFileSync(DESTINATION, "utf8")).toBe("two")
    })
})
