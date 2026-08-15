import type { ToolchainKind } from "../installables"
import type { Instances } from "../instances"
import type { ToolchainId } from "./toolchain-ids"

export interface Toolchain {
    kind: ToolchainKind
    id: ToolchainId
    instances: Instances
}
