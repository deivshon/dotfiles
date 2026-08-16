import type { InstallError, VerificationError } from "../errors"
import { isExecutableInPath } from "../installs/verification"
import type { Result } from "../shared/result"
import type {
    ArchLinuxSystemApplicationId,
    MacOsSystemApplicationId,
    UserApplicationId,
    WindowsSystemApplicationId,
} from "../types/applications/application-ids"
import type {
    ArchLinuxSystemApplication,
    MacOsSystemApplication,
    UserApplication,
    WindowsSystemApplication,
} from "../types/applications/applications"
import type { Configs, FileCopyConfig, JsonMergeConfig } from "../types/configs"
import type { ExtensionId } from "../types/extensions/extension-ids"
import type { Extension } from "../types/extensions/extensions"
import type { Installable } from "../types/installables"
import type {
    ArchLinuxCustomInstance,
    ArchLinuxPackageInstance,
    Instances,
    MacOsCustomInstance,
    MacOsPackageInstance,
} from "../types/instances"
import type { Library } from "../types/libraries/libraries"
import type { LibraryId } from "../types/libraries/library-ids"
import type { ToolchainId } from "../types/toolchains/toolchain-ids"
import type { Toolchain } from "../types/toolchains/toolchains"

interface CustomInstanceOptions {
    install: () => Promise<Result<void, InstallError>>
    isInstalled: () => Promise<Result<boolean, VerificationError>>
    requires: Installable[]
}

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the application, and name of its executable
 * @param configs Config files of the application
 * @description Builds an Arch Linux application that the operating system provides.
 */
export const archLinuxSystemApplication = <TId extends ArchLinuxSystemApplicationId>(
    id: TId,
    configs: Configs = [],
): ArchLinuxSystemApplication & { id: TId } => ({
    kind: "application",
    type: "system",
    platform: "arch-linux",
    id,
    instance: {
        platform: "arch-linux",
        isInstalled: isExecutableInPath(id),
    },
    configs,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the application, and name of its executable
 * @param configs Config files of the application
 * @description Builds a macOS application that the operating system provides.
 */
export const macOsSystemApplication = <TId extends MacOsSystemApplicationId>(
    id: TId,
    configs: Configs = [],
): MacOsSystemApplication & { id: TId } => ({
    kind: "application",
    type: "system",
    platform: "mac-os",
    id,
    instance: {
        platform: "mac-os",
        isInstalled: isExecutableInPath(id),
    },
    configs,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the application, and name of its executable
 * @param configs Config files of the application
 * @description Builds a Windows application that the operating system provides.
 */
export const windowsSystemApplication = <TId extends WindowsSystemApplicationId>(
    id: TId,
    configs: Configs = [],
): WindowsSystemApplication & { id: TId } => ({
    kind: "application",
    type: "system",
    platform: "windows",
    id,
    instance: {
        platform: "windows",
        isInstalled: isExecutableInPath(id),
    },
    configs,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the application
 * @param instances Instance of every platform, `null` where the application is unavailable
 * @param configs Config files of the application
 * @description Builds an application that the user installs, with one instance per platform.
 */
export const userApplication = <TId extends UserApplicationId>(
    id: TId,
    instances: Instances,
    configs: Configs = [],
): UserApplication & { id: TId } => ({
    kind: "application",
    type: "user",
    id,
    instances,
    configs,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the library
 * @param instances Instance of every platform, `null` where the library is unavailable
 * @description Builds a library that other installables depend on, with one instance per platform.
 */
export const library = <TId extends LibraryId>(
    id: TId,
    instances: Instances,
): Library & { id: TId } => ({
    kind: "library",
    id,
    instances,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the toolchain
 * @param instances Instance of every platform, `null` where the toolchain is unavailable
 * @description Builds a toolchain that a toolchain manager installs, with one instance per platform.
 */
export const toolchain = <TId extends ToolchainId>(
    id: TId,
    instances: Instances,
): Toolchain & { id: TId } => ({
    kind: "toolchain",
    id,
    instances,
})

/**
 * @template TId Literal identifier that the result keeps
 * @param id Identifier of the extension
 * @param instances Instance of every platform, `null` where the extension is unavailable
 * @description Builds an extension that a host application installs, with one instance per platform.
 */
export const extension = <TId extends ExtensionId>(
    id: TId,
    instances: Instances,
): Extension & { id: TId } => ({
    kind: "extension",
    id,
    instances,
})

/**
 * @param source Segments of the path of the file, from the root of the repository
 * @param destination Segments of the path of the file on this machine
 * @description Builds a config file that the run copies as it is.
 */
export const fileCopy = (source: string[], destination: string[]): FileCopyConfig => ({
    type: "file-copy",
    source,
    destination,
})

/**
 * @param source Segments of the path of the file, from the root of the repository
 * @param destination Segments of the path of the file on this machine
 * @description Builds a config file that the run merges into the file of this machine.
 * @remarks Both files must hold a JSON object. The values of the repository win.
 */
export const jsonMerge = (source: string[], destination: string[]): JsonMergeConfig => ({
    type: "json-merge",
    source,
    destination,
})

/**
 * @param packageName Name of the package
 * @description Builds an instance that `pacman` installs from the standard repositories.
 */
export const pacmanPackage = (packageName: string): ArchLinuxPackageInstance => ({
    platform: "arch-linux",
    install: {
        type: "package",
        platform: "arch-linux",
        manager: "pacman",
        aur: false,
        packageName,
        requires: [["application", "pacman"]],
    },
})

/**
 * @param packageName Name of the package
 * @description Builds an instance that `paru` installs from the AUR.
 */
export const paruPackage = (packageName: string): ArchLinuxPackageInstance => ({
    platform: "arch-linux",
    install: {
        type: "package",
        platform: "arch-linux",
        manager: "paru",
        aur: true,
        packageName,
        requires: [["application", "paru"]],
    },
})

/**
 * @param packageName Name of the formula
 * @description Builds an instance that Homebrew installs as a formula.
 */
export const brewFormula = (packageName: string): MacOsPackageInstance => ({
    platform: "mac-os",
    install: {
        type: "package",
        manager: "brew",
        cask: false,
        packageName,
        requires: [["application", "brew"]],
    },
})

/**
 * @param packageName Token of the cask
 * @description Builds an instance that Homebrew installs as a cask.
 */
export const brewCask = (packageName: string): MacOsPackageInstance => ({
    platform: "mac-os",
    install: {
        type: "package",
        manager: "brew",
        cask: true,
        packageName,
        requires: [["application", "brew"]],
    },
})

/**
 * @param options Install command, verification command, and required installables
 * @description Builds an Arch Linux instance with an install that no package manager covers.
 */
export const archLinuxCustomInstall = ({
    install,
    isInstalled,
    requires,
}: CustomInstanceOptions): ArchLinuxCustomInstance => ({
    platform: "arch-linux",
    install: { type: "custom", install, requires },
    isInstalled,
})

/**
 * @param options Install command, verification command, and required installables
 * @description Builds a macOS instance with an install that no package manager covers.
 */
export const macOsCustomInstall = ({
    install,
    isInstalled,
    requires,
}: CustomInstanceOptions): MacOsCustomInstance => ({
    platform: "mac-os",
    install: { type: "custom", install, requires },
    isInstalled,
})
