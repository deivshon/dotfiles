import { describe, expect, it } from "vitest"

import type { Installable } from "../types/installables"
import { formatInstallable, installableId, installableKey } from "./installables"

const cases: Array<{ installable: Installable; key: string; id: string }> = [
    { installable: ["application", "git"], key: "application:git", id: "git" },
    {
        installable: ["library", "base-devel"],
        key: "library:base-devel",
        id: "base-devel",
    },
    {
        installable: ["toolchain", "rust-stable"],
        key: "toolchain:rust-stable",
        id: "rust-stable",
    },
    {
        installable: ["extension", "oxc-vscode"],
        key: "extension:oxc-vscode",
        id: "oxc-vscode",
    },
]

describe("installableKey", () => {
    it.each(cases)(
        "joins the kind and the identifier of $key",
        ({ installable, key }) => {
            expect(installableKey(installable)).toBe(key)
        },
    )

    it("gives a different key to the same identifier of another kind", () => {
        expect(installableKey(["application", "pacman"])).not.toBe(
            installableKey(["library", "base-devel"]),
        )
    })
})

describe("installableId", () => {
    it.each(cases)("returns the identifier of $key", ({ installable, id }) => {
        expect(installableId(installable)).toBe(id)
    })
})

describe("formatInstallable", () => {
    it.each(cases)("labels $key", ({ installable, key }) => {
        const [kind, id] = key.split(":")
        expect(formatInstallable(installable)).toBe(`${kind} "${id}"`)
    })
})
