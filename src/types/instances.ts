import type { VerificationError } from "../errors"
import type { Result } from "../shared/result"
import type {
    ArchLinuxCustomInstall,
    ArchLinuxPackageInstall,
    MacOsCustomInstall,
    MacOsPackageInstall,
    WindowsCustomInstall,
    WindowsPackageInstall,
} from "./installs"
import type {
    ArchLinuxPlatform,
    MacOsPlatform,
    Platform,
    WindowsPlatform,
} from "./platforms"

type IsInstalled = () => Promise<Result<boolean, VerificationError>>

export interface ArchLinuxPackageInstance {
    platform: ArchLinuxPlatform
    install: ArchLinuxPackageInstall
}
export interface ArchLinuxCustomInstance {
    platform: ArchLinuxPlatform
    install: ArchLinuxCustomInstall
    isInstalled: IsInstalled
}
export interface ArchLinuxSystemInstance {
    platform: ArchLinuxPlatform
    isInstalled: IsInstalled
}

export interface MacOsPackageInstance {
    platform: MacOsPlatform
    install: MacOsPackageInstall
}
export interface MacOsCustomInstance {
    platform: MacOsPlatform
    install: MacOsCustomInstall
    isInstalled: IsInstalled
}
export interface MacOsSystemInstance {
    platform: MacOsPlatform
    isInstalled: IsInstalled
}

export interface WindowsPackageInstance {
    platform: WindowsPlatform
    install: WindowsPackageInstall
}
export interface WindowsCustomInstance {
    platform: WindowsPlatform
    install: WindowsCustomInstall
    isInstalled: IsInstalled
}
export interface WindowsSystemInstance {
    platform: WindowsPlatform
    isInstalled: IsInstalled
}

export type Instance =
    | ArchLinuxPackageInstance
    | ArchLinuxCustomInstance
    | MacOsPackageInstance
    | MacOsCustomInstance
    | WindowsPackageInstance
    | WindowsCustomInstance

export type SystemInstance =
    | ArchLinuxSystemInstance
    | MacOsSystemInstance
    | WindowsSystemInstance

export type Instances = {
    [K in Platform]: Extract<Instance, { platform: K }> | null
}
