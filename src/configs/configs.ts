import { createHash } from "node:crypto"
import { existsSync } from "node:fs"
import { mkdir, readFile, rename, writeFile } from "node:fs/promises"
import path from "node:path"

import { pipe } from "es-toolkit/fp"

import { CONFIG_BACKUP_PREFIX, CONFIG_HASH_ALGORITHM } from "../consts"
import type { ConfigError, FileSystemFailed } from "../errors"
import { Result } from "../shared/result"
import type { ConfigResult, ConfigTarget, ConfigTargetBase } from "../types/configs"
import { mergeJson } from "./json-merge"

/**
 * @param target Path of the file
 * @param cause Value that the failure carries
 * @param message Text for the reader
 * @description Builds the error of a file operation that did not complete.
 */
const fileSystemFailed = (
    target: string,
    cause: unknown,
    message: string,
): FileSystemFailed => ({
    type: "file-system-failed",
    path: target,
    cause,
    message,
})

/**
 * @param filePath Path of the file
 * @description Reads the content of the config file of the repository.
 */
const readSource = (filePath: string): Promise<Result<Buffer, FileSystemFailed>> =>
    Result.tryAsync(
        () => readFile(filePath),
        cause =>
            fileSystemFailed(
                filePath,
                cause,
                `The config file "${filePath}" was not read`,
            ),
    )

/**
 * @param filePath Path of the file
 * @description Reads the content of a file, and returns `null` when the file is absent.
 */
const readIfPresent = (
    filePath: string,
): Promise<Result<Buffer | null, FileSystemFailed>> =>
    Result.tryAsync(
        () => (existsSync(filePath) ? readFile(filePath) : Promise.resolve(null)),
        cause => fileSystemFailed(filePath, cause, `The file "${filePath}" was not read`),
    )

const hashOf = (content: Buffer): string =>
    createHash(CONFIG_HASH_ALGORITHM).update(content).digest("hex")

const backupPathOf = (destination: string): string =>
    `${destination}${CONFIG_BACKUP_PREFIX}${Date.now()}`

/**
 * @param target Type, source, and destination of one config file
 * @param destination Content of the destination, `null` when the file is absent
 * @description Builds the content that the destination holds after the run.
 * @remarks A merge of an absent destination is a copy of the source.
 */
const desiredContentOf = async (
    target: ConfigTargetBase,
    destination: Buffer | null,
): Promise<Result<Buffer, ConfigError>> => {
    const source = await readSource(target.source)
    if (!source.success || target.type === "file-copy" || destination === null) {
        return source
    }

    return pipe(
        mergeJson(
            target.source,
            source.value.toString(),
            target.destination,
            destination.toString(),
        ),
        Result.map(text => Buffer.from(text)),
    )
}

/**
 * @param target Type, source, and destination of one config file
 * @description True when the destination holds the content that the run writes.
 * @remarks An unreadable file is never current, so the run reports the error of the copy.
 */
export const isConfigCurrent = async (target: ConfigTargetBase): Promise<boolean> => {
    const destination = await readIfPresent(target.destination)
    if (!destination.success || destination.value === null) {
        return false
    }

    const desired = await desiredContentOf(target, destination.value)
    return desired.success && hashOf(desired.value) === hashOf(destination.value)
}

/**
 * @param target Config file of the plan
 * @description Writes the config file to its destination, and returns the outcome.
 * @remarks Renames a destination of a different content before the write, so no data is lost.
 */
export const applyConfig = async (
    target: ConfigTarget,
): Promise<Result<ConfigResult, ConfigError>> => {
    const destination = await readIfPresent(target.destination)
    if (!destination.success) {
        return destination
    }

    const desired = await desiredContentOf(target, destination.value)
    if (!desired.success) {
        return desired
    }

    if (
        destination.value !== null &&
        hashOf(destination.value) === hashOf(desired.value)
    ) {
        return Result.ok({ target, status: "unchanged", backupPath: null })
    }

    const backupPath =
        destination.value === null ? null : backupPathOf(target.destination)

    return Result.tryAsync(
        async (): Promise<ConfigResult> => {
            await mkdir(path.dirname(target.destination), { recursive: true })
            if (backupPath !== null) {
                await rename(target.destination, backupPath)
            }
            await writeFile(target.destination, desired.value)

            return {
                target,
                status: backupPath === null ? "copied" : "replaced",
                backupPath,
            }
        },
        cause =>
            fileSystemFailed(
                target.destination,
                cause,
                `The config file "${target.source}" was not written to "${target.destination}"`,
            ),
    )
}
