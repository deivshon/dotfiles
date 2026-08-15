import type { ApplicationKind } from "../installables"
import type {
    ArchLinuxSystemInstance,
    Instances,
    MacOsSystemInstance,
    WindowsSystemInstance,
} from "../instances"
import type { ArchLinuxPlatform, MacOsPlatform, WindowsPlatform } from "../platforms"
import type { SystemApplicationId, UserApplicationId } from "./application-ids"

export type UserApplicationType = "user"
export type SystemApplicationType = "system"

export interface UserApplication {
    kind: ApplicationKind
    type: UserApplicationType
    id: UserApplicationId
    instances: Instances
}

export interface ArchLinuxSystemApplication {
    kind: ApplicationKind
    type: SystemApplicationType
    platform: ArchLinuxPlatform
    id: SystemApplicationId
    instance: ArchLinuxSystemInstance
}
export interface MacOsSystemApplication {
    kind: ApplicationKind
    type: SystemApplicationType
    platform: MacOsPlatform
    id: SystemApplicationId
    instance: MacOsSystemInstance
}
export interface WindowsSystemApplication {
    kind: ApplicationKind
    type: SystemApplicationType
    platform: WindowsPlatform
    id: SystemApplicationId
    instance: WindowsSystemInstance
}
export type SystemApplication =
    | ArchLinuxSystemApplication
    | MacOsSystemApplication
    | WindowsSystemApplication

export type Application = UserApplication | SystemApplication
