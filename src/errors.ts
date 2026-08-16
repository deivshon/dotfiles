import type { Installable } from "./types/installables"
import type { Platform } from "./types/platforms"

export interface CommandNotRun {
    type: "command-not-run"
    command: string
    cause: unknown
    message: string
}

export interface CommandFailed {
    type: "command-failed"
    command: string
    exitCode: number | null
    output: string
    message: string
}

export interface FileSystemFailed {
    type: "file-system-failed"
    path: string
    cause: unknown
    message: string
}

export interface DownloadFailed {
    type: "download-failed"
    url: string
    cause: unknown
    message: string
}

export interface InstallRejected {
    type: "install-rejected"
    source: string
    message: string
}

export interface ConfigNotMerged {
    type: "config-not-merged"
    path: string
    message: string
}

export interface InstallableUnavailable {
    type: "installable-unavailable"
    installable: Installable
    platform: Platform
    message: string
}

export interface UnsupportedInstall {
    type: "unsupported-install"
    installable: Installable
    message: string
}

export interface DependencyCycle {
    type: "dependency-cycle"
    path: Installable[]
    message: string
}

export type CommandError = CommandNotRun | CommandFailed
export type VerificationError = CommandError
export type InstallError =
    | CommandError
    | FileSystemFailed
    | DownloadFailed
    | InstallRejected
export type ConfigError = FileSystemFailed | ConfigNotMerged
export type PlanError =
    | VerificationError
    | InstallableUnavailable
    | UnsupportedInstall
    | DependencyCycle
