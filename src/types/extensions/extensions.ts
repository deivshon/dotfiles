import type { ExtensionKind } from "../installables"
import type { Instances } from "../instances"
import type { ExtensionId } from "./extension-ids"

export interface Extension {
    kind: ExtensionKind
    id: ExtensionId
    instances: Instances
}
