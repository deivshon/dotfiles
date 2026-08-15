import type { SpawnOptions } from "node:child_process"

import { pipe } from "es-toolkit/fp"
import { exec } from "es-toolkit/server"

import type { CommandError, CommandFailed, CommandNotRun } from "./errors"
import { Result } from "./shared/result"

interface RunOptions {
    cwd?: string
}

const formatCommand = (command: string, args: string[]): string =>
    [command, ...args].join(" ")

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @param spawnOptions Options of the child process
 * @description Starts a command, and returns its outcome whatever its exit code.
 * @remarks Only a command that does not start is an error here.
 */
const spawnCommand = (command: string, args: string[], spawnOptions: SpawnOptions) =>
    Result.tryAsync(
        () => exec(command, args, { throwOnNonZeroExitCode: false, spawnOptions }),
        (cause): CommandNotRun => ({
            type: "command-not-run",
            command: formatCommand(command, args),
            cause,
            message: `The command "${formatCommand(command, args)}" did not start`,
        }),
    )

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @param exitCode Code of the child process
 * @param output Standard error of the child process
 * @description Builds the error of a command that exited with a non-zero code.
 */
const commandFailed = (
    command: string,
    args: string[],
    exitCode: number | null,
    output: string,
): CommandFailed => ({
    type: "command-failed",
    command: formatCommand(command, args),
    exitCode,
    output,
    message: `The command "${formatCommand(command, args)}" exited with code ${exitCode}`,
})

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @param options Working directory of the child process
 * @description Runs a command with the terminal attached to the child process.
 * @remarks The output of the command stays on the terminal and is not returned.
 */
export const runInteractively = async (
    command: string,
    args: string[],
    options: RunOptions = {},
): Promise<Result<void, CommandError>> =>
    pipe(
        await spawnCommand(command, args, { stdio: "inherit", cwd: options.cwd }),
        Result.bind(result =>
            result.exitCode === 0
                ? Result.ok(undefined)
                : Result.err(commandFailed(command, args, result.exitCode, "")),
        ),
    )

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @param options Working directory of the child process
 * @description Runs a command and returns its standard output.
 */
export const runQuietly = async (
    command: string,
    args: string[],
    options: RunOptions = {},
): Promise<Result<string, CommandError>> =>
    pipe(
        await spawnCommand(command, args, { cwd: options.cwd }),
        Result.bind(result =>
            result.exitCode === 0
                ? Result.ok(result.stdout)
                : Result.err(
                      commandFailed(command, args, result.exitCode, result.stderr),
                  ),
        ),
    )

/**
 * @param command Executable name
 * @param args Arguments of the command
 * @description Returns true when the command exits with code 0.
 * @remarks A non-zero exit code is an answer here, not an error.
 */
export const commandSucceeds = async (
    command: string,
    args: string[],
): Promise<Result<boolean, CommandNotRun>> =>
    pipe(
        await spawnCommand(command, args, {}),
        Result.map(result => result.exitCode === 0),
    )
