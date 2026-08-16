import { describe, expect, it } from "vitest"

import { mergeJson } from "./json-merge"

const merge = (source: string, destination: string) =>
    mergeJson("/repo/source.json", source, "/home/user/destination.json", destination)

const mergedText = (source: string, destination: string): string => {
    const result = merge(source, destination)
    if (!result.success) {
        throw new Error(result.error.message)
    }
    return result.value
}

const mergedValue = (source: string, destination: string): unknown =>
    JSON.parse(mergedText(source, destination))

describe("mergeJson", () => {
    it("adds a key that the destination leaves out", () => {
        expect(mergedValue('{"a":1}', "{}")).toEqual({ a: 1 })
    })

    it("lets the value of the repository win", () => {
        expect(mergedValue('{"a":1}', '{"a":2}')).toEqual({ a: 1 })
    })

    it("keeps a key that the source leaves out", () => {
        expect(mergedValue('{"a":1}', '{"b":2}')).toEqual({ a: 1, b: 2 })
    })

    it("returns the destination when the source is empty", () => {
        expect(mergedText("{}", '{\n    "a": 1\n}')).toBe('{\n    "a": 1\n}')
    })

    it("merges nested objects key by key", () => {
        expect(
            mergedValue('{"editor":{"tabSize":4}}', '{"editor":{"fontSize":12}}'),
        ).toEqual({ editor: { tabSize: 4, fontSize: 12 } })
    })

    it("merges deeply nested objects", () => {
        expect(mergedValue('{"a":{"b":{"c":1}}}', '{"a":{"b":{"d":2}}}')).toEqual({
            a: { b: { c: 1, d: 2 } },
        })
    })

    it("builds the missing branch of a nested key", () => {
        expect(mergedValue('{"a":{"b":{"c":1}}}', "{}")).toEqual({ a: { b: { c: 1 } } })
    })

    it("replaces an array instead of joining it", () => {
        expect(mergedValue('{"list":[1,2]}', '{"list":[3,4,5]}')).toEqual({
            list: [1, 2],
        })
    })

    it("treats an empty object of the source as a leaf", () => {
        expect(mergedValue('{"a":{}}', '{"a":{"b":1}}')).toEqual({ a: {} })
    })

    it("replaces an object of the destination with a scalar of the source", () => {
        expect(mergedValue('{"a":1}', '{"a":{"b":2}}')).toEqual({ a: 1 })
    })

    it("reports a source that nests a key under a scalar of the destination", () => {
        expect(merge('{"a":{"b":2}}', '{"a":1}')).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: "/home/user/destination.json",
                message:
                    'The values of "/repo/source.json" do not fit the shape of "/home/user/destination.json"',
            },
        })
    })

    it.each([
        { name: "a string", value: '"text"' },
        { name: "a number", value: "42" },
        { name: "a negative number", value: "-1.5" },
        { name: "true", value: "true" },
        { name: "false", value: "false" },
        { name: "null", value: "null" },
        { name: "an empty array", value: "[]" },
        { name: "an array of objects", value: '[{"a":1}]' },
    ])("writes $name as a value", ({ value }) => {
        expect(mergedValue(`{"key":${value}}`, "{}")).toEqual({
            key: JSON.parse(value),
        })
    })

    it("keeps a trailing comma of the destination", () => {
        expect(mergedText('{"b":2}', '{\n    "a": 1,\n}')).toContain('"a": 1')
    })

    it("reads comments in the source", () => {
        expect(mergedValue('{\n    // note\n    "a": 1\n}', "{}")).toEqual({ a: 1 })
    })

    it("leaves the comments of the source out of the destination", () => {
        expect(mergedText('{\n    // source note\n    "a": 1\n}', "{}")).not.toContain(
            "source note",
        )
    })
})

describe("mergeJson and the comments of the destination", () => {
    it("keeps a line comment above the key that the merge overwrites", () => {
        const destination = ["{", "    // about a", '    "a": 1', "}"].join("\n")

        expect(mergedText('{"a":2}', destination)).toBe(
            ["{", "    // about a", '    "a": 2', "}"].join("\n"),
        )
    })

    it("keeps a trailing comment on the line of the key that the merge overwrites", () => {
        const destination = ["{", '    "a": 1 // about a', "}"].join("\n")

        expect(mergedText('{"a":2}', destination)).toBe(
            ["{", '    "a": 2 // about a', "}"].join("\n"),
        )
    })

    it("keeps a block comment above the key that the merge overwrites", () => {
        const destination = ["{", "    /* about a */", '    "a": 1', "}"].join("\n")

        expect(mergedText('{"a":2}', destination)).toBe(
            ["{", "    /* about a */", '    "a": 2', "}"].join("\n"),
        )
    })

    it("keeps the header comment of the file", () => {
        const destination = ["// header", "{", '    "a": 1', "}"].join("\n")

        expect(mergedText('{"a":2}', destination)).toBe(
            ["// header", "{", '    "a": 2', "}"].join("\n"),
        )
    })

    it("keeps a comment that sits between two keys", () => {
        const destination = [
            "{",
            '    "a": 1,',
            "    // between",
            '    "b": 2',
            "}",
        ].join("\n")

        expect(mergedText('{"b":9}', destination)).toBe(
            ["{", '    "a": 1,', "    // between", '    "b": 9', "}"].join("\n"),
        )
    })

    it("keeps a comment of a key that the source leaves out", () => {
        const destination = [
            "{",
            "    // about a",
            '    "a": 1,',
            '    "b": 2',
            "}",
        ].join("\n")

        expect(mergedText('{"b":9}', destination)).toBe(
            ["{", "    // about a", '    "a": 1,', '    "b": 9', "}"].join("\n"),
        )
    })

    it("keeps a comment inside a nested object", () => {
        const destination = [
            "{",
            '    "editor": {',
            "        // about tabSize",
            '        "tabSize": 2',
            "    }",
            "}",
        ].join("\n")

        expect(mergedText('{"editor":{"tabSize":4}}', destination)).toBe(
            [
                "{",
                '    "editor": {',
                "        // about tabSize",
                '        "tabSize": 4',
                "    }",
                "}",
            ].join("\n"),
        )
    })

    it("keeps the comment of a sibling key when the merge adds a nested key", () => {
        const destination = [
            "{",
            '    "editor": {',
            "        // about fontSize",
            '        "fontSize": 12',
            "    }",
            "}",
        ].join("\n")
        const merged = mergedText('{"editor":{"tabSize":4}}', destination)

        expect(merged).toContain("// about fontSize")
        expect(merged.indexOf("// about fontSize")).toBeLessThan(
            merged.indexOf('"fontSize"'),
        )
        expect(JSON.parse(merged.replaceAll(/\s*\/\/[^\n]*/gu, ""))).toEqual({
            editor: { fontSize: 12, tabSize: 4 },
        })
    })

    it("keeps every comment of a destination that the merge changes in many places", () => {
        const destination = [
            "// header",
            "{",
            "    // about a",
            '    "a": 1,',
            '    "b": 2, // about b',
            "    /* about c */",
            '    "c": {',
            "        // about d",
            '        "d": 4',
            "    }",
            "}",
        ].join("\n")
        const merged = mergedText('{"a":9,"b":8,"c":{"d":7}}', destination)

        expect(merged).toBe(
            [
                "// header",
                "{",
                "    // about a",
                '    "a": 9,',
                '    "b": 8, // about b',
                "    /* about c */",
                '    "c": {',
                "        // about d",
                '        "d": 7',
                "    }",
                "}",
            ].join("\n"),
        )
    })

    it("keeps a comment that sits after the last key", () => {
        const destination = ["{", '    "a": 1', "    // tail", "}"].join("\n")
        const merged = mergedText('{"a":2}', destination)

        expect(merged).toContain("// tail")
        expect(merged.indexOf('"a": 2')).toBeLessThan(merged.indexOf("// tail"))
    })

    it("keeps a comment that sits below the closing brace", () => {
        const destination = ["{", '    "a": 1', "}", "// footer"].join("\n")

        expect(mergedText('{"a":2}', destination)).toBe(
            ["{", '    "a": 2', "}", "// footer"].join("\n"),
        )
    })

    it("keeps the comments of a merge that changes nothing", () => {
        const destination = ["{", "    // about a", '    "a": 1', "}"].join("\n")

        expect(mergedText('{"a":1}', destination)).toBe(destination)
    })

    it("indents a new key with four spaces", () => {
        expect(mergedText('{"a":1}', "{}")).toBe('{\n    "a": 1\n}')
    })

    it("keeps the order of the keys of the destination", () => {
        const merged = mergedText('{"b":9}', '{\n    "b": 1,\n    "a": 2\n}')

        expect(merged.indexOf('"b"')).toBeLessThan(merged.indexOf('"a"'))
    })

    it("applies every leaf of the source", () => {
        expect(mergedValue('{"a":1,"b":{"c":2},"d":[3]}', '{"e":4}')).toEqual({
            a: 1,
            b: { c: 2 },
            d: [3],
            e: 4,
        })
    })

    it("handles a key that holds a dot", () => {
        expect(mergedValue('{"editor.tabSize":4}', "{}")).toEqual({
            "editor.tabSize": 4,
        })
    })

    it("returns the destination unchanged when both files are equal", () => {
        const text = '{\n    "a": 1\n}'

        expect(mergedText(text, text)).toBe(text)
    })

    it("names the source in the error of a source that is not valid JSON", () => {
        expect(merge("{", "{}")).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: "/repo/source.json",
                message: 'The file "/repo/source.json" is not valid JSON',
            },
        })
    })

    it("names the destination in the error of a destination that is not valid JSON", () => {
        expect(merge("{}", "{")).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: "/home/user/destination.json",
                message: 'The file "/home/user/destination.json" is not valid JSON',
            },
        })
    })

    it("reads the source before the destination", () => {
        const result = merge("{", "{")

        expect(!result.success && result.error.path).toBe("/repo/source.json")
    })

    it.each([
        { name: "an array", text: "[1,2]" },
        { name: "a string", text: '"text"' },
        { name: "a number", text: "42" },
        { name: "null", text: "null" },
    ])("rejects a source that holds $name", ({ text }) => {
        expect(merge(text, "{}")).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: "/repo/source.json",
                message: 'The file "/repo/source.json" holds no JSON object',
            },
        })
    })

    it("rejects a destination that holds no object", () => {
        expect(merge("{}", "[]")).toEqual({
            success: false,
            error: {
                type: "config-not-merged",
                path: "/home/user/destination.json",
                message: 'The file "/home/user/destination.json" holds no JSON object',
            },
        })
    })
})
