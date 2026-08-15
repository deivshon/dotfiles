import type { LibraryKind } from "../installables"
import type { Instances } from "../instances"
import type { LibraryId } from "./library-ids"

export interface Library {
    kind: LibraryKind
    id: LibraryId
    instances: Instances
}
