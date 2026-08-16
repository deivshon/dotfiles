import { tmpdir } from "node:os"
import path from "node:path"

import { beforeEach, describe, expect, it, vi } from "vitest"

import { Result } from "../shared/result"

const runInteractively = vi.hoisted(() => vi.fn())
const question = vi.hoisted(() => vi.fn())
const close = vi.hoisted(() => vi.fn())

vi.mock("../process", () => ({ runInteractively }))
vi.mock("node:fs/promises", async () => {
    const { fs } = await import("memfs")
    return { ...fs.promises, default: fs.promises }
})
vi.mock("node:readline/promises", () => ({
    createInterface: () => ({ question, close }),
}))

const { vol } = await import("memfs")
const {
    installArchLinuxPackageFromAurManual,
    installArchLinuxPackagesFromAurParu,
    installArchLinuxPackagesFromStandardRepos,
    installFromGit,
    installFromScript,
    installHomebrewCaskPackages,
    installHomebrewFormulaePackages,
    installRustupToolchain,
    installVsCodeExtension,
} = await import("./installs")

const TEMPORARY_ROOT = tmpdir()

const okRun = Result.ok(undefined)

const commandFailed = {
    type: "command-failed" as const,
    command: "git clone",
    exitCode: 1,
    output: "",
    message: "The command failed",
}

/** @description Returns every temporary directory that the volume still holds. */
const temporaryDirectories = (): string[] =>
    Object.keys(vol.toJSON())
        .flatMap(entry =>
            entry
                .slice(TEMPORARY_ROOT.length + 1)
                .split(path.sep)
                .slice(0, 1),
        )
        .filter(entry => entry.startsWith("dotfiles-"))

const respond = (body: string, status = 200): Response => new Response(body, { status })

beforeEach(() => {
    vol.reset()
    vol.mkdirSync(TEMPORARY_ROOT, { recursive: true })
    runInteractively.mockReset()
    question.mockReset()
    close.mockReset()
})

describe("package manager installs", () => {
    const packageCases = [
        {
            name: "the standard Arch Linux repositories",
            install: installArchLinuxPackagesFromStandardRepos,
            command: "sudo",
            args: ["pacman", "-S", "--needed"],
        },
        {
            name: "the AUR through paru",
            install: installArchLinuxPackagesFromAurParu,
            command: "paru",
            args: ["-S", "--needed"],
        },
        {
            name: "Homebrew formulae",
            install: installHomebrewFormulaePackages,
            command: "brew",
            args: ["install", "--formula"],
        },
        {
            name: "Homebrew casks",
            install: installHomebrewCaskPackages,
            command: "brew",
            args: ["install", "--cask"],
        },
    ]

    it.each(packageCases)(
        "installs from $name with one command",
        async ({ install, command, args }) => {
            runInteractively.mockResolvedValue(okRun)

            await install(["git", "bat"])()

            expect(runInteractively).toHaveBeenCalledExactlyOnceWith(command, [
                ...args,
                "git",
                "bat",
            ])
        },
    )

    it.each(packageCases)("does not run $name before the call", ({ install }) => {
        install(["git"])

        expect(runInteractively).not.toHaveBeenCalled()
    })

    it("keeps the order of the package names", async () => {
        runInteractively.mockResolvedValue(okRun)

        await installArchLinuxPackagesFromStandardRepos(["c", "a", "b"])()

        expect(runInteractively).toHaveBeenCalledExactlyOnceWith("sudo", [
            "pacman",
            "-S",
            "--needed",
            "c",
            "a",
            "b",
        ])
    })

    it("returns the error of a command that failed", async () => {
        runInteractively.mockResolvedValue(Result.err(commandFailed))

        await expect(
            installArchLinuxPackagesFromStandardRepos(["git"])(),
        ).resolves.toEqual({ success: false, error: commandFailed })
    })
})

describe("installRustupToolchain", () => {
    it("installs the channel with rustup", async () => {
        runInteractively.mockResolvedValue(okRun)

        await installRustupToolchain("nightly")()

        expect(runInteractively).toHaveBeenCalledExactlyOnceWith("rustup", [
            "toolchain",
            "install",
            "nightly",
        ])
    })
})

describe("installVsCodeExtension", () => {
    it("installs the extension with the code executable", async () => {
        runInteractively.mockResolvedValue(okRun)

        await installVsCodeExtension("oxc.oxc-vscode")()

        expect(runInteractively).toHaveBeenCalledExactlyOnceWith("code", [
            "--install-extension",
            "oxc.oxc-vscode",
        ])
    })
})

describe("installArchLinuxPackageFromAurManual", () => {
    it("clones the repository, then builds it in the clone", async () => {
        runInteractively.mockResolvedValue(okRun)

        await installArchLinuxPackageFromAurManual("https://aur.archlinux.org/paru.git")()

        const buildDirectory = runInteractively.mock.calls[0]?.[1]?.[2]
        expect(runInteractively.mock.calls).toEqual([
            ["git", ["clone", "https://aur.archlinux.org/paru.git", buildDirectory]],
            ["makepkg", ["-si"], { cwd: buildDirectory }],
        ])
        expect(buildDirectory).toContain(path.join(TEMPORARY_ROOT, "dotfiles-"))
    })

    it("erases the build directory after a run that worked", async () => {
        runInteractively.mockResolvedValue(okRun)

        await installArchLinuxPackageFromAurManual("url")()

        expect(temporaryDirectories()).toEqual([])
    })

    it("does not build when the clone fails", async () => {
        runInteractively.mockResolvedValue(Result.err(commandFailed))

        const result = await installArchLinuxPackageFromAurManual("url")()

        expect(runInteractively).toHaveBeenCalledOnce()
        expect(result).toEqual({ success: false, error: commandFailed })
    })

    it("erases the build directory after a clone that failed", async () => {
        runInteractively.mockResolvedValue(Result.err(commandFailed))

        await installArchLinuxPackageFromAurManual("url")()

        expect(temporaryDirectories()).toEqual([])
    })

    it("returns a file-system error when the temporary directory is absent", async () => {
        vol.reset()

        const result = await installArchLinuxPackageFromAurManual("url")()

        expect(result).toEqual({
            success: false,
            error: {
                type: "file-system-failed",
                path: TEMPORARY_ROOT,
                cause: expect.anything(),
                message: "The temporary directory was not created",
            },
        })
        expect(runInteractively).not.toHaveBeenCalled()
    })
})

describe("installFromScript", () => {
    beforeEach(() => {
        vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond("echo hello")))
        vi.stubEnv("VISUAL", "")
        vi.stubEnv("EDITOR", "")
    })

    it("downloads the script, reviews it, then runs it after approval", async () => {
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("y")

        const result = await installFromScript("https://example.test/install.sh")()

        const scriptPath = runInteractively.mock.calls[0]?.[1]?.[0]
        expect(runInteractively.mock.calls).toEqual([
            ["vi", [scriptPath]],
            ["bash", [scriptPath]],
        ])
        expect(scriptPath).toContain(path.join(TEMPORARY_ROOT, "dotfiles-"))
        expect(scriptPath).toContain("install.sh")
        expect(result).toEqual(okRun)
    })

    it("asks the user with the address of the script", async () => {
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("y")

        await installFromScript("https://example.test/install.sh")()

        expect(question).toHaveBeenCalledExactlyOnceWith(
            "Run the script from https://example.test/install.sh? [y/N] ",
        )
        expect(close).toHaveBeenCalledOnce()
    })

    it("opens the editor of the VISUAL variable", async () => {
        vi.stubEnv("VISUAL", "nvim")
        vi.stubEnv("EDITOR", "nano")
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("n")

        await installFromScript("url")()

        expect(runInteractively.mock.calls[0]?.[0]).toBe("nvim")
    })

    it("opens the editor of the EDITOR variable when VISUAL is empty", async () => {
        vi.stubEnv("EDITOR", "nano")
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("n")

        await installFromScript("url")()

        expect(runInteractively.mock.calls[0]?.[0]).toBe("nano")
    })

    it.each(["n", "", "yes", "Y ", " y"])(
        "accepts the answer %j only when it reads y",
        async answer => {
            runInteractively.mockResolvedValue(okRun)
            question.mockResolvedValue(answer)

            const result = await installFromScript("url")()
            const approved = answer.trim().toLowerCase() === "y"

            expect(runInteractively).toHaveBeenCalledTimes(approved ? 2 : 1)
            expect(result.success).toBe(approved)
        },
    )

    it("returns an install-rejected error on a refusal", async () => {
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("n")

        await expect(installFromScript("https://example.test/x.sh")()).resolves.toEqual({
            success: false,
            error: {
                type: "install-rejected",
                source: "https://example.test/x.sh",
                message: 'The script from "https://example.test/x.sh" was not approved',
            },
        })
    })

    it("writes the script with the owner-only mode", async () => {
        runInteractively.mockImplementation(async (command: string, args: string[]) => {
            if (command === "vi" && args.length > 0) {
                const target = args[0]
                expect(target).toBeDefined()
                expect(vol.readFileSync(String(target), "utf8")).toBe("echo hello")
                expect(vol.statSync(String(target)).mode & 0o777).toBe(0o700)
            }
            return okRun
        })
        question.mockResolvedValue("n")

        await installFromScript("url")()

        expect.assertions(3)
    })

    it("erases the temporary directory after the run", async () => {
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("y")

        await installFromScript("url")()

        expect(temporaryDirectories()).toEqual([])
    })

    it("does not ask the user when the review command fails", async () => {
        runInteractively.mockResolvedValue(Result.err(commandFailed))

        const result = await installFromScript("url")()

        expect(question).not.toHaveBeenCalled()
        expect(result).toEqual({ success: false, error: commandFailed })
    })

    it("returns a download error when the request throws", async () => {
        const cause = new Error("offline")
        vi.stubGlobal("fetch", vi.fn().mockRejectedValue(cause))

        await expect(installFromScript("https://example.test/x.sh")()).resolves.toEqual({
            success: false,
            error: {
                type: "download-failed",
                url: "https://example.test/x.sh",
                cause,
                message: 'The download of "https://example.test/x.sh" failed',
            },
        })
        expect(runInteractively).not.toHaveBeenCalled()
    })

    it("returns a download error on a status that is not ok", async () => {
        vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond("not found", 404)))

        await expect(installFromScript("https://example.test/x.sh")()).resolves.toEqual({
            success: false,
            error: {
                type: "download-failed",
                url: "https://example.test/x.sh",
                cause: 404,
                message:
                    'The download of "https://example.test/x.sh" returned the status 404',
            },
        })
    })

    it("returns a download error when the body is not read", async () => {
        const cause = new Error("broken stream")
        vi.stubGlobal(
            "fetch",
            vi.fn().mockResolvedValue({
                ok: true,
                status: 200,
                text: () => Promise.reject(cause),
            }),
        )

        await expect(installFromScript("https://example.test/x.sh")()).resolves.toEqual({
            success: false,
            error: {
                type: "download-failed",
                url: "https://example.test/x.sh",
                cause,
                message: 'The body of "https://example.test/x.sh" was not read',
            },
        })
    })

    it("downloads the script on every call", async () => {
        const download = vi.fn().mockResolvedValue(respond("echo hello"))
        vi.stubGlobal("fetch", download)
        runInteractively.mockResolvedValue(okRun)
        question.mockResolvedValue("n")
        const install = installFromScript("url")

        expect(download).not.toHaveBeenCalled()

        await install()
        await install()

        expect(download).toHaveBeenCalledTimes(2)
    })
})

describe("installFromGit", () => {
    const options = {
        repoUrl: "https://github.test/owner/tool.git",
        buildCommand: "cargo",
        buildArgs: ["build", "--release", "--locked"],
        artifactPath: path.join("target", "release", "tool"),
        destinationPath: path.join(TEMPORARY_ROOT, "bin", "tool"),
    }

    const withArtifact = () =>
        runInteractively.mockImplementation(
            async (command: string, _args: string[], run?: { cwd: string }) => {
                if (command === "cargo" && run !== undefined) {
                    vol.mkdirSync(path.join(run.cwd, "target", "release"), {
                        recursive: true,
                    })
                    vol.writeFileSync(
                        path.join(run.cwd, "target", "release", "tool"),
                        "binary",
                    )
                }
                return okRun
            },
        )

    it("clones with a shallow clone, then builds in the clone", async () => {
        withArtifact()

        await installFromGit(options)()

        const buildDirectory = runInteractively.mock.calls[0]?.[1]?.[4]
        expect(runInteractively.mock.calls).toEqual([
            ["git", ["clone", "--depth", "1", options.repoUrl, buildDirectory]],
            ["cargo", ["build", "--release", "--locked"], { cwd: buildDirectory }],
        ])
    })

    it("copies the artifact to its destination as an executable", async () => {
        withArtifact()

        const result = await installFromGit(options)()

        expect(result).toEqual({ success: true, value: undefined })
        expect(vol.readFileSync(options.destinationPath, "utf8")).toBe("binary")
        expect(vol.statSync(options.destinationPath).mode & 0o777).toBe(0o755)
    })

    it("erases the build directory after the copy", async () => {
        withArtifact()

        await installFromGit(options)()

        expect(temporaryDirectories()).toEqual([])
    })

    it("does not build when the clone fails", async () => {
        runInteractively.mockResolvedValue(Result.err(commandFailed))

        const result = await installFromGit(options)()

        expect(runInteractively).toHaveBeenCalledOnce()
        expect(result).toEqual({ success: false, error: commandFailed })
    })

    it("does not copy when the build fails", async () => {
        runInteractively.mockImplementation(async (command: string) =>
            command === "git" ? okRun : Result.err(commandFailed),
        )

        const result = await installFromGit(options)()

        expect(result).toEqual({ success: false, error: commandFailed })
        expect(vol.existsSync(options.destinationPath)).toBe(false)
    })

    it("returns a file-system error when the artifact is absent", async () => {
        runInteractively.mockResolvedValue(okRun)

        const result = await installFromGit(options)()

        expect(result).toEqual({
            success: false,
            error: {
                type: "file-system-failed",
                path: options.destinationPath,
                cause: expect.anything(),
                message: expect.stringContaining(
                    `was not copied to "${options.destinationPath}"`,
                ),
            },
        })
    })
})
