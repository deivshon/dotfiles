import { beforeEach, describe, expect, it, vi } from "vitest"

const exec = vi.hoisted(() => vi.fn())
const reportCommand = vi.hoisted(() => vi.fn())

vi.mock("es-toolkit/server", async importOriginal => ({
    ...(await importOriginal<typeof import("es-toolkit/server")>()),
    exec,
}))
vi.mock("./report", () => ({ reportCommand }))

const { commandSucceeds, runInteractively, runQuietly } = await import("./process")

interface ExecResult {
    pid: number | undefined
    stdout: string
    stderr: string
    exitCode: number | null
}

const execResult = (overrides: Partial<ExecResult> = {}): ExecResult => ({
    pid: 1,
    stdout: "",
    stderr: "",
    exitCode: 0,
    ...overrides,
})

beforeEach(() => {
    exec.mockReset()
    reportCommand.mockReset()
})

describe("runInteractively", () => {
    it("attaches the terminal to the child process", async () => {
        exec.mockResolvedValue(execResult())

        await runInteractively("pacman", ["-S", "git"])

        expect(exec).toHaveBeenCalledExactlyOnceWith("pacman", ["-S", "git"], {
            throwOnNonZeroExitCode: false,
            spawnOptions: { stdio: "inherit", cwd: undefined },
        })
    })

    it("forwards the working directory", async () => {
        exec.mockResolvedValue(execResult())

        await runInteractively("makepkg", ["-si"], { cwd: "/tmp/build" })

        expect(exec).toHaveBeenCalledExactlyOnceWith("makepkg", ["-si"], {
            throwOnNonZeroExitCode: false,
            spawnOptions: { stdio: "inherit", cwd: "/tmp/build" },
        })
    })

    it("echoes the command before it starts", async () => {
        exec.mockResolvedValue(execResult())

        await runInteractively("git", ["clone", "url"])

        expect(reportCommand).toHaveBeenCalledExactlyOnceWith("git", ["clone", "url"])
    })

    it("returns a successful result on exit code 0", async () => {
        exec.mockResolvedValue(execResult())

        await expect(runInteractively("git", [])).resolves.toEqual({
            success: true,
            value: undefined,
        })
    })

    it("returns a command-failed error on a non-zero exit code", async () => {
        exec.mockResolvedValue(execResult({ exitCode: 2, stderr: "ignored" }))

        await expect(runInteractively("git", ["clone", "url"])).resolves.toEqual({
            success: false,
            error: {
                type: "command-failed",
                command: "git clone url",
                exitCode: 2,
                output: "",
                message: 'The command "git clone url" exited with code 2',
            },
        })
    })

    it("returns a command-failed error on a null exit code", async () => {
        exec.mockResolvedValue(execResult({ exitCode: null }))

        const result = await runInteractively("git", [])

        expect(result.success).toBe(false)
        expect(!result.success && result.error.message).toBe(
            'The command "git" exited with code null',
        )
    })

    it("returns a command-not-run error when the command does not start", async () => {
        const cause = new Error("ENOENT")
        exec.mockRejectedValue(cause)

        await expect(runInteractively("missing", ["-v"])).resolves.toEqual({
            success: false,
            error: {
                type: "command-not-run",
                command: "missing -v",
                cause,
                message: 'The command "missing -v" did not start',
            },
        })
    })
})

describe("runQuietly", () => {
    it("captures the output instead of the terminal", async () => {
        exec.mockResolvedValue(execResult({ stdout: "git\n" }))

        await runQuietly("pacman", ["-Qnq"])

        expect(exec).toHaveBeenCalledExactlyOnceWith("pacman", ["-Qnq"], {
            throwOnNonZeroExitCode: false,
            spawnOptions: { cwd: undefined },
        })
    })

    it("does not echo the command", async () => {
        exec.mockResolvedValue(execResult())

        await runQuietly("pacman", ["-Qnq"])

        expect(reportCommand).not.toHaveBeenCalled()
    })

    it("returns the standard output on exit code 0", async () => {
        exec.mockResolvedValue(execResult({ stdout: "git\nbat\n" }))

        await expect(runQuietly("pacman", ["-Qnq"])).resolves.toEqual({
            success: true,
            value: "git\nbat\n",
        })
    })

    it("carries the standard error into the failure", async () => {
        exec.mockResolvedValue(execResult({ exitCode: 1, stderr: "no database" }))

        await expect(runQuietly("pacman", ["-Qnq"])).resolves.toEqual({
            success: false,
            error: {
                type: "command-failed",
                command: "pacman -Qnq",
                exitCode: 1,
                output: "no database",
                message: 'The command "pacman -Qnq" exited with code 1',
            },
        })
    })

    it("forwards the working directory", async () => {
        exec.mockResolvedValue(execResult())

        await runQuietly("git", ["status"], { cwd: "/repo" })

        expect(exec).toHaveBeenCalledExactlyOnceWith("git", ["status"], {
            throwOnNonZeroExitCode: false,
            spawnOptions: { cwd: "/repo" },
        })
    })
})

describe("commandSucceeds", () => {
    it("returns true on exit code 0", async () => {
        exec.mockResolvedValue(execResult())

        await expect(commandSucceeds("which", ["git"])).resolves.toEqual({
            success: true,
            value: true,
        })
    })

    it("returns false on a non-zero exit code", async () => {
        exec.mockResolvedValue(execResult({ exitCode: 1 }))

        await expect(commandSucceeds("which", ["git"])).resolves.toEqual({
            success: true,
            value: false,
        })
    })

    it("returns an error only when the command does not start", async () => {
        exec.mockRejectedValue(new Error("ENOENT"))

        const result = await commandSucceeds("which", ["git"])

        expect(result.success).toBe(false)
        expect(!result.success && result.error.type).toBe("command-not-run")
    })

    it("passes no spawn options", async () => {
        exec.mockResolvedValue(execResult())

        await commandSucceeds("which", ["git"])

        expect(exec).toHaveBeenCalledExactlyOnceWith("which", ["git"], {
            throwOnNonZeroExitCode: false,
            spawnOptions: {},
        })
    })
})
