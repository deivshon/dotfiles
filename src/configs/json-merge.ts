import { isPlainObject } from "es-toolkit"
import { applyEdits, modify, parse } from "jsonc-parser"
import type { ModificationOptions, ParseError } from "jsonc-parser"
import { z } from "zod"

import { CONFIG_INDENT_SIZE } from "../consts"
import type { ConfigNotMerged } from "../errors"
import { Result } from "../shared/result"

const jsonObjectSchema = z.record(z.string(), z.json())

type JsonObject = z.infer<typeof jsonObjectSchema>
type JsonValue = JsonObject[string]

interface Leaf {
    path: string[]
    value: JsonValue
}

const MODIFICATION_OPTIONS: ModificationOptions = {
    formattingOptions: { tabSize: CONFIG_INDENT_SIZE, insertSpaces: true },
}

/**
 * @param filePath Path of the file
 * @param message Text for the reader
 * @description Builds the error of a file that no merge can read.
 */
const notMerged = (filePath: string, message: string): ConfigNotMerged => ({
    type: "config-not-merged",
    path: filePath,
    message,
})

/**
 * @param filePath Path of the file
 * @param text Body of the file
 * @description Reads the file as a JSON object that holds comments and trailing commas.
 */
const parseJsonObject = (
    filePath: string,
    text: string,
): Result<JsonObject, ConfigNotMerged> => {
    const errors: ParseError[] = []
    const value: unknown = parse(text, errors, { allowTrailingComma: true })
    if (errors.length > 0) {
        return Result.err(notMerged(filePath, `The file "${filePath}" is not valid JSON`))
    }

    const object = jsonObjectSchema.safeParse(value)
    return object.success
        ? Result.ok(object.data)
        : Result.err(notMerged(filePath, `The file "${filePath}" holds no JSON object`))
}

/**
 * @param object Object of the config file
 * @param prefix Path of the object in its document
 * @description Returns the path and the value of every leaf of the object.
 * @remarks An array is a leaf, so the value of the repository replaces the value of the machine.
 */
const leavesOf = (object: JsonObject, prefix: string[]): Leaf[] =>
    Object.entries(object).flatMap(([key, value]) =>
        isPlainObject(value) && !Array.isArray(value) && Object.keys(value).length > 0
            ? leavesOf(value, prefix.concat(key))
            : [{ path: prefix.concat(key), value }],
    )

/**
 * @param sourcePath Path of the config file of the repository
 * @param sourceText Body of the config file of the repository
 * @param destinationPath Path of the config file of this machine
 * @param destinationText Body of the config file of this machine
 * @description Returns the body of the machine file with every value of the repository file set.
 * @remarks Keeps the comments, the order, and the formatting of the values that the repository file leaves out.
 */
export const mergeJson = (
    sourcePath: string,
    sourceText: string,
    destinationPath: string,
    destinationText: string,
): Result<string, ConfigNotMerged> => {
    const source = parseJsonObject(sourcePath, sourceText)
    if (!source.success) {
        return source
    }

    const destination = parseJsonObject(destinationPath, destinationText)
    if (!destination.success) {
        return destination
    }

    return Result.try(
        () =>
            leavesOf(source.value, []).reduce(
                (text, leaf) =>
                    applyEdits(
                        text,
                        modify(text, leaf.path, leaf.value, MODIFICATION_OPTIONS),
                    ),
                destinationText,
            ),
        () =>
            notMerged(
                destinationPath,
                `The values of "${sourcePath}" do not fit the shape of "${destinationPath}"`,
            ),
    )
}
