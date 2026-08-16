import { describe, expect, it, vi } from "vitest"

import { Result } from "./result"

describe("Result.ok", () => {
    it("wraps the value", () => {
        expect(Result.ok(1)).toEqual({ success: true, value: 1 })
    })

    it("keeps a nullish value", () => {
        expect(Result.ok(null)).toEqual({ success: true, value: null })
        expect(Result.ok(undefined)).toEqual({ success: true, value: undefined })
    })
})

describe("Result.err", () => {
    it("wraps the error", () => {
        expect(Result.err("boom")).toEqual({ success: false, error: "boom" })
    })
})

describe("Result.try", () => {
    it("returns the value of a function that does not throw", () => {
        expect(Result.try(() => 2, String)).toEqual({ success: true, value: 2 })
    })

    it("maps the thrown value to an error", () => {
        const cause = new Error("no")
        const onThrow = vi.fn(() => "mapped")

        expect(
            Result.try(() => {
                throw cause
            }, onThrow),
        ).toEqual({ success: false, error: "mapped" })
        expect(onThrow).toHaveBeenCalledExactlyOnceWith(cause)
    })

    it("catches a thrown value that is not an error", () => {
        const throwText = (): never => {
            throw "text"
        }

        expect(Result.try(throwText, cause => cause)).toEqual({
            success: false,
            error: "text",
        })
    })
})

describe("Result.tryAsync", () => {
    it("returns the value of a promise that resolves", async () => {
        await expect(Result.tryAsync(() => Promise.resolve(3), String)).resolves.toEqual({
            success: true,
            value: 3,
        })
    })

    it("maps the rejection value to an error", async () => {
        const cause = new Error("no")

        await expect(
            Result.tryAsync(
                () => Promise.reject(cause),
                thrown => thrown,
            ),
        ).resolves.toEqual({ success: false, error: cause })
    })

    it("catches a function that throws before it returns the promise", async () => {
        await expect(
            Result.tryAsync(() => {
                throw new Error("sync")
            }, String),
        ).resolves.toEqual({ success: false, error: "Error: sync" })
    })
})

describe("Result.map", () => {
    it("maps the value of a successful result", () => {
        expect(Result.map((value: number) => value + 1)(Result.ok(1))).toEqual({
            success: true,
            value: 2,
        })
    })

    it("leaves a failed result alone", () => {
        const mapValue = vi.fn()
        const failure = Result.err("boom")

        expect(Result.map(mapValue)(failure)).toBe(failure)
        expect(mapValue).not.toHaveBeenCalled()
    })
})

describe("Result.mapErr", () => {
    it("maps the error of a failed result", () => {
        expect(
            Result.mapErr((error: string) => error.length)(Result.err("boom")),
        ).toEqual({ success: false, error: 4 })
    })

    it("leaves a successful result alone", () => {
        const mapError = vi.fn()
        const success = Result.ok(1)

        expect(Result.mapErr(mapError)(success)).toBe(success)
        expect(mapError).not.toHaveBeenCalled()
    })
})

describe("Result.bind", () => {
    it("chains onto a successful result", () => {
        expect(
            Result.bind((value: number) => Result.ok(value * 2))(Result.ok(2)),
        ).toEqual({ success: true, value: 4 })
    })

    it("returns the error of the chained operation", () => {
        expect(Result.bind(() => Result.err("next"))(Result.ok(2))).toEqual({
            success: false,
            error: "next",
        })
    })

    it("leaves a failed result alone", () => {
        const next = vi.fn()
        const failure = Result.err("first")

        expect(Result.bind(next)(failure)).toBe(failure)
        expect(next).not.toHaveBeenCalled()
    })
})

describe("Result.unwrapOr", () => {
    it("returns the value of a successful result", () => {
        expect(Result.unwrapOr(0)(Result.ok(5))).toBe(5)
    })

    it("returns the fallback of a failed result", () => {
        expect(Result.unwrapOr(0)(Result.err("boom"))).toBe(0)
    })
})

describe("Result.sequence", () => {
    it("returns an empty list for an empty input", () => {
        expect(Result.sequence([])).toEqual({ success: true, value: [] })
    })

    it("keeps the order of the values", () => {
        expect(Result.sequence([Result.ok(1), Result.ok(2), Result.ok(3)])).toEqual({
            success: true,
            value: [1, 2, 3],
        })
    })

    it("returns the first error", () => {
        expect(
            Result.sequence([Result.ok(1), Result.err("first"), Result.err("second")]),
        ).toEqual({ success: false, error: "first" })
    })
})
