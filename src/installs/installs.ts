import { chmod, copyFile, mkdir, mkdtemp, rm, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import path from "node:path"
import { env, stdin, stdout } from "node:process"
import { createInterface } from "node:readline/promises"

import {
    BASH_EXECUTABLE,
    BREW_EXECUTABLE,
    EXECUTABLE_FILE_MODE,
    FALLBACK_EDITOR,
    GIT_EXECUTABLE,
    INSTALL_SCRIPT_FILE_NAME,
    MAKEPKG_EXECUTABLE,
    PACMAN_EXECUTABLE,
    PARU_EXECUTABLE,
    RUSTUP_EXECUTABLE,
    SUDO_EXECUTABLE,
    TEMPORARY_DIRECTORY_PREFIX,
    VS_CODE_EXECUTABLE,
} from "../consts"
import type {
    DownloadFailed,
    FileSystemFailed,
    InstallError,
    InstallRejected,
} from "../errors"
import { runInteractively } from "../process"
import { Result } from "../shared/result"

interface GitInstallOptions {
    repoUrl: string
    buildCommand: string
    buildArgs: string[]
    artifactPath: string
    destinationPath: string
}

/** @description Builds an empty directory for the files of one install. */
const makeTemporaryDirectory = (): Promise<Result<string, FileSystemFailed>> =>
    Result.tryAsync(
        () => mkdtemp(path.join(tmpdir(), TEMPORARY_DIRECTORY_PREFIX)),
        (cause): FileSystemFailed => ({
            type: "file-system-failed",
            path: tmpdir(),
            cause,
            message: "The temporary directory was not created",
        }),
    )

/**
 * @param target Path to erase
 * @description Erases a path and its content.
 * @remarks Never fails, because a cleanup error must not hide the outcome of the install.
 */
const removeQuietly = async (target: string): Promise<void> => {
    await rm(target, { recursive: true, force: true }).catch(() => undefined)
}

/**
 * @param url Address of the download
 * @param cause Value that the failure carries
 * @param message Text for the reader
 * @description Builds the error of a download that did not complete.
 */
const downloadFailed = (
    url: string,
    cause: unknown,
    message: string,
): DownloadFailed => ({
    type: "download-failed",
    url,
    cause,
    message,
})

/**
 * @param url Address of the file
 * @description Fetches the body of a file as text.
 */
const downloadText = async (url: string): Promise<Result<string, DownloadFailed>> => {
    const response = await Result.tryAsync(
        () => fetch(url),
        cause => downloadFailed(url, cause, `The download of "${url}" failed`),
    )
    if (!response.success) {
        return response
    }

    if (!response.value.ok) {
        return Result.err(
            downloadFailed(
                url,
                response.value.status,
                `The download of "${url}" returned the status ${response.value.status}`,
            ),
        )
    }

    return Result.tryAsync(
        () => response.value.text(),
        cause => downloadFailed(url, cause, `The body of "${url}" was not read`),
    )
}

/**
 * @param directory Directory of the file
 * @param content Body of the script
 * @description Writes the script to the directory, and returns its path.
 * @remarks The mode of the file is `0o700`, so only its owner can read it and run it.
 */
const writeScript = (
    directory: string,
    content: string,
): Promise<Result<string, FileSystemFailed>> => {
    const scriptPath = path.join(directory, INSTALL_SCRIPT_FILE_NAME)
    return Result.tryAsync(
        async () => {
            await writeFile(scriptPath, content, { mode: 0o700 })
            return scriptPath
        },
        (cause): FileSystemFailed => ({
            type: "file-system-failed",
            path: scriptPath,
            cause,
            message: `The install script was not written to "${scriptPath}"`,
        }),
    )
}

/**
 * @param source Path of the built file
 * @param destination Path of the installed file
 * @description Copies the built file to its destination, and makes it executable.
 * @remarks Builds the directory of the destination when it is absent.
 */
const copyExecutable = (
    source: string,
    destination: string,
): Promise<Result<void, FileSystemFailed>> =>
    Result.tryAsync(
        async () => {
            await mkdir(path.dirname(destination), { recursive: true })
            await copyFile(source, destination)
            await chmod(destination, EXECUTABLE_FILE_MODE)
        },
        (cause): FileSystemFailed => ({
            type: "file-system-failed",
            path: destination,
            cause,
            message: `The file "${source}" was not copied to "${destination}"`,
        }),
    )

const reviewInEditor = (scriptPath: string) =>
    runInteractively(env.VISUAL || env.EDITOR || FALLBACK_EDITOR, [scriptPath])

/**
 * @param url Address of the script
 * @description Asks the user to approve the script, and returns the answer.
 * @remarks The answer loses its spaces and its case, and every answer other than `y` is a refusal.
 */
const askForApproval = async (url: string): Promise<boolean> => {
    const readline = createInterface({ input: stdin, output: stdout })
    try {
        const answer = await readline.question(`Run the script from ${url}? [y/N] `)
        return answer.trim().toLowerCase() === "y"
    } finally {
        readline.close()
    }
}

/**
 * @param packageNames Names of the packages
 * @description Installs packages from the standard Arch Linux repositories with `pacman`.
 */
export const installArchLinuxPackagesFromStandardRepos =
    (packageNames: string[]) => (): Promise<Result<void, InstallError>> =>
        runInteractively(SUDO_EXECUTABLE, [
            PACMAN_EXECUTABLE,
            "-S",
            "--needed",
            ...packageNames,
        ])

/**
 * @param repoUrl Clone URL of the AUR repository
 * @description Builds and installs an AUR package from its repository with `makepkg`.
 * @remarks Bootstraps the AUR helper itself, when no AUR helper exists yet.
 */
export const installArchLinuxPackageFromAurManual =
    (repoUrl: string) => async (): Promise<Result<void, InstallError>> => {
        const buildDirectory = await makeTemporaryDirectory()
        if (!buildDirectory.success) {
            return buildDirectory
        }

        try {
            const clone = await runInteractively(GIT_EXECUTABLE, [
                "clone",
                repoUrl,
                buildDirectory.value,
            ])
            if (!clone.success) {
                return clone
            }

            return await runInteractively(MAKEPKG_EXECUTABLE, ["-si"], {
                cwd: buildDirectory.value,
            })
        } finally {
            await removeQuietly(buildDirectory.value)
        }
    }

/**
 * @param packageNames Names of the packages
 * @description Installs AUR packages with the `paru` helper.
 * @remarks `paru` calls `sudo` itself and refuses to run as root.
 */
export const installArchLinuxPackagesFromAurParu =
    (packageNames: string[]) => (): Promise<Result<void, InstallError>> =>
        runInteractively(PARU_EXECUTABLE, ["-S", "--needed", ...packageNames])

/**
 * @param packageNames Names of the formulae
 * @description Installs Homebrew formulae.
 */
export const installHomebrewFormulaePackages =
    (packageNames: string[]) => (): Promise<Result<void, InstallError>> =>
        runInteractively(BREW_EXECUTABLE, ["install", "--formula", ...packageNames])

/**
 * @param packageNames Tokens of the casks
 * @description Installs Homebrew casks.
 */
export const installHomebrewCaskPackages =
    (packageNames: string[]) => (): Promise<Result<void, InstallError>> =>
        runInteractively(BREW_EXECUTABLE, ["install", "--cask", ...packageNames])

/**
 * @param channel Name of the release channel
 * @description Installs a Rust toolchain with `rustup`.
 */
export const installRustupToolchain =
    (channel: string) => (): Promise<Result<void, InstallError>> =>
        runInteractively(RUSTUP_EXECUTABLE, ["toolchain", "install", channel])

/**
 * @param extensionId Identifier of the extension in the marketplace
 * @description Installs a Visual Studio Code extension.
 */
export const installVsCodeExtension =
    (extensionId: string) => (): Promise<Result<void, InstallError>> =>
        runInteractively(VS_CODE_EXECUTABLE, ["--install-extension", extensionId])

/**
 * @param url Address of the script
 * @description Downloads a shell script, shows it in the editor, then runs it after approval.
 * @remarks Fails with `InstallRejected` when the answer is not `y`.
 */
export const installFromScript =
    (url: string) => async (): Promise<Result<void, InstallError>> => {
        const script = await downloadText(url)
        if (!script.success) {
            return script
        }

        const directory = await makeTemporaryDirectory()
        if (!directory.success) {
            return directory
        }

        try {
            const scriptPath = await writeScript(directory.value, script.value)
            if (!scriptPath.success) {
                return scriptPath
            }

            const review = await reviewInEditor(scriptPath.value)
            if (!review.success) {
                return review
            }

            if (!(await askForApproval(url))) {
                return Result.err<InstallRejected>({
                    type: "install-rejected",
                    source: url,
                    message: `The script from "${url}" was not approved`,
                })
            }

            return await runInteractively(BASH_EXECUTABLE, [scriptPath.value])
        } finally {
            await removeQuietly(directory.value)
        }
    }

/**
 * @param options Repository, build command, artifact path, and destination path
 * @description Clones a repository, builds it, then copies the artifact to its destination.
 * @remarks The artifact path is relative to the root of the repository.
 */
export const installFromGit =
    ({
        repoUrl,
        buildCommand,
        buildArgs,
        artifactPath,
        destinationPath,
    }: GitInstallOptions) =>
    async (): Promise<Result<void, InstallError>> => {
        const buildDirectory = await makeTemporaryDirectory()
        if (!buildDirectory.success) {
            return buildDirectory
        }

        try {
            const clone = await runInteractively(GIT_EXECUTABLE, [
                "clone",
                "--depth",
                "1",
                repoUrl,
                buildDirectory.value,
            ])
            if (!clone.success) {
                return clone
            }

            const build = await runInteractively(buildCommand, buildArgs, {
                cwd: buildDirectory.value,
            })
            if (!build.success) {
                return build
            }

            return await copyExecutable(
                path.join(buildDirectory.value, artifactPath),
                destinationPath,
            )
        } finally {
            await removeQuietly(buildDirectory.value)
        }
    }
