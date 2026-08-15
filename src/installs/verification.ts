import { pipe } from "es-toolkit/fp"
import { match, P } from "ts-pattern"

import {
    BREW_EXECUTABLE,
    PACMAN_EXECUTABLE,
    RUSTUP_EXECUTABLE,
    VS_CODE_EXECUTABLE,
    WHERE_EXECUTABLE,
    WHICH_EXECUTABLE,
} from "../consts"
import type { VerificationError } from "../errors"
import { commandSucceeds, runQuietly } from "../process"
import { platform } from "../shared/platform"
import { Result } from "../shared/result"

/**
 * @param command Executable of the package manager
 * @param args Arguments that list the packages
 * @description Returns the command that reads the package list, one name per line.
 */
const listPackages =
    (command: string, args: string[]) =>
    async (): Promise<Result<string[], VerificationError>> =>
        pipe(
            await runQuietly(command, args),
            Result.map(stdout =>
                stdout
                    .split("\n")
                    .map(line => line.trim())
                    .filter(line => line.length > 0),
            ),
        )

/**
 * @param list Command that reads the package list
 * @description Returns the command that looks for one package in the list.
 * @remarks The match is exact, so the name must have the form that the package manager prints.
 */
const isPackageInList =
    (list: () => Promise<Result<string[], VerificationError>>) =>
    (packageName: string) =>
    async (): Promise<Result<boolean, VerificationError>> =>
        pipe(
            await list(),
            Result.map(packageNames => packageNames.includes(packageName)),
        )

/**
 * @param executableName Name of the executable
 * @description Returns true when the executable is reachable through the `PATH`.
 */
export const isExecutableInPath =
    (executableName: string) => (): Promise<Result<boolean, VerificationError>> =>
        commandSucceeds(
            match(platform)
                .with(P.union("arch-linux", "mac-os"), () => WHICH_EXECUTABLE)
                .with("windows", () => WHERE_EXECUTABLE)
                .exhaustive(),
            [executableName],
        )

/** @description Returns the packages installed from the standard Arch Linux repositories. */
export const listStandardArchLinuxPackages = listPackages(PACMAN_EXECUTABLE, ["-Qnq"])

/** @description Returns the packages installed from the AUR. */
export const listAurArchLinuxPackages = listPackages(PACMAN_EXECUTABLE, ["-Qmq"])

/** @description Returns the installed Homebrew formulae. */
export const listBrewFormulaePackages = listPackages(BREW_EXECUTABLE, [
    "list",
    "--formula",
    "-1",
])

/** @description Returns the installed Homebrew casks. */
export const listBrewCaskPackages = listPackages(BREW_EXECUTABLE, [
    "list",
    "--cask",
    "-1",
])

/**
 * @param packageName Name of the package
 * @description Returns true when the package comes from a standard Arch Linux repository.
 */
export const isStandardArchLinuxPackageInstalled = isPackageInList(
    listStandardArchLinuxPackages,
)

/**
 * @param packageName Name of the package
 * @description Returns true when the package comes from the AUR.
 */
export const isAurArchLinuxPackageInstalled = isPackageInList(listAurArchLinuxPackages)

/**
 * @param packageName Name of the formula
 * @description Returns true when the Homebrew formula is installed.
 */
export const isBrewFormulaePackageInstalled = isPackageInList(listBrewFormulaePackages)

/**
 * @param packageName Token of the cask
 * @description Returns true when the Homebrew cask is installed.
 */
export const isBrewCaskPackageInstalled = isPackageInList(listBrewCaskPackages)

/** @description Returns the installed Rust toolchains. */
export const listRustupToolchains = listPackages(RUSTUP_EXECUTABLE, ["toolchain", "list"])

/** @description Returns the installed Visual Studio Code extensions. */
export const listVsCodeExtensions = listPackages(VS_CODE_EXECUTABLE, [
    "--list-extensions",
])

/**
 * @param channel Name of the release channel
 * @description Returns true when the Rust toolchain of the channel is installed.
 * @remarks `rustup` appends the target triple to the channel, so the match is a prefix match.
 */
export const isRustupToolchainInstalled =
    (channel: string) => async (): Promise<Result<boolean, VerificationError>> =>
        pipe(
            await listRustupToolchains(),
            Result.map(toolchains =>
                toolchains.some(toolchain => toolchain.startsWith(channel)),
            ),
        )

/**
 * @param extensionId Identifier of the extension in the marketplace
 * @description Returns true when the Visual Studio Code extension is installed.
 */
export const isVsCodeExtensionInstalled = isPackageInList(listVsCodeExtensions)
