import type { Application, UserApplication } from "./applications/applications"
import type { Extension } from "./extensions/extensions"
import type { Library } from "./libraries/libraries"
import type { Toolchain } from "./toolchains/toolchains"

export type InstancedEntity = UserApplication | Library | Toolchain | Extension

export type InstallableEntity = Application | Library | Toolchain | Extension
