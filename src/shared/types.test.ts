import { describe, expectTypeOf, it } from "vitest"

import type { Exclude, Select } from "./types"

type Manager = "pacman" | "paru" | "brew"

describe("Select", () => {
    it("returns the chosen member", () => {
        expectTypeOf<Select<Manager, "pacman">>().toEqualTypeOf<"pacman">()
    })

    it("returns the whole union when the choice is the union", () => {
        expectTypeOf<Select<Manager, Manager>>().toEqualTypeOf<Manager>()
    })

    it("returns a union of two members", () => {
        expectTypeOf<Select<Manager, "pacman" | "paru">>().toEqualTypeOf<
            "pacman" | "paru"
        >()
    })
})

describe("Exclude", () => {
    it("removes one member of the union", () => {
        expectTypeOf<Exclude<Manager, "brew">>().toEqualTypeOf<"pacman" | "paru">()
    })

    it("removes two members of the union", () => {
        expectTypeOf<Exclude<Manager, "brew" | "paru">>().toEqualTypeOf<"pacman">()
    })

    it("returns never when it removes every member", () => {
        expectTypeOf<Exclude<Manager, Manager>>().toEqualTypeOf<never>()
    })
})
