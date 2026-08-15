import type { ApplicationId } from "./applications/application-ids"
import type { ExtensionId } from "./extensions/extension-ids"
import type { LibraryId } from "./libraries/library-ids"
import type { ToolchainId } from "./toolchains/toolchain-ids"

export type ApplicationKind = "application"
export type LibraryKind = "library"
export type ToolchainKind = "toolchain"
export type ExtensionKind = "extension"

export type InstallableKind =
    | ApplicationKind
    | LibraryKind
    | ToolchainKind
    | ExtensionKind

export type InstallableId = ApplicationId | LibraryId | ToolchainId | ExtensionId

export type Installable =
    | [ApplicationKind, ApplicationId]
    | [LibraryKind, LibraryId]
    | [ToolchainKind, ToolchainId]
    | [ExtensionKind, ExtensionId]

export type InstallableKey = `${InstallableKind}:${InstallableId}`
