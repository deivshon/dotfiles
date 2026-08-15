import type { InstallError } from "../errors"
import type { Result } from "../shared/result"
import type { Select } from "../shared/types"
import type { ApplicationId } from "./applications/application-ids"
import type { ApplicationKind, Installable } from "./installables"
import type { ArchLinuxPlatform } from "./platforms"

export type PackageInstallType = "package"
export type CustomInstallType = "custom"
export type InstallType = PackageInstallType | CustomInstallType

export type ArchLinuxPackageManager = "pacman" | "paru"
export type MacOsPackageManager = "brew"
export type WindowsPackageManager = "winget"
export type PackageManager =
    | ArchLinuxPackageManager
    | MacOsPackageManager
    | WindowsPackageManager

export interface ArchLinuxStandardPackageInstall {
    type: PackageInstallType
    manager: Select<ArchLinuxPackageManager, "pacman">
    platform: ArchLinuxPlatform
    packageName: string
    aur: false
    requires: [[ApplicationKind, Select<ApplicationId, "pacman">]]
}
export interface ArchLinuxAurPackageInstall {
    type: PackageInstallType
    manager: Select<ArchLinuxPackageManager, "paru">
    platform: ArchLinuxPlatform
    packageName: string
    aur: true
    requires: [[ApplicationKind, Select<ApplicationId, "paru">]]
}
export type ArchLinuxPackageInstall =
    | ArchLinuxStandardPackageInstall
    | ArchLinuxAurPackageInstall

export interface MacOsPackageInstall {
    type: PackageInstallType
    manager: MacOsPackageManager
    packageName: string
    cask: boolean
    requires: [[ApplicationKind, Select<ApplicationId, "brew">]]
}

export interface WindowsPackageInstall {
    type: PackageInstallType
    manager: WindowsPackageManager
    packageName: string
    requires: [[ApplicationKind, Select<ApplicationId, "winget">]]
}

export type PackageInstall =
    | ArchLinuxPackageInstall
    | MacOsPackageInstall
    | WindowsPackageInstall

export interface ArchLinuxCustomInstall {
    type: CustomInstallType
    install: () => Promise<Result<void, InstallError>>
    requires: Installable[]
}

export interface MacOsCustomInstall {
    type: CustomInstallType
    install: () => Promise<Result<void, InstallError>>
    requires: Installable[]
}

export interface WindowsCustomInstall {
    type: CustomInstallType
    install: () => Promise<Result<void, InstallError>>
    requires: Installable[]
}

export type CustomInstall =
    | ArchLinuxCustomInstall
    | MacOsCustomInstall
    | WindowsCustomInstall

export type ArchLinuxInstall = ArchLinuxPackageInstall | ArchLinuxCustomInstall
export type MacOsInstall = MacOsPackageInstall | MacOsCustomInstall
export type WindowsInstall = WindowsPackageInstall | WindowsCustomInstall
