import type { Installable, InstallableId, InstallableKey } from "../types/installables"

/**
 * @param installable Kind and identifier of the installable
 * @description Returns the unique key of the installable.
 */
export const installableKey = ([kind, id]: Installable): InstallableKey => `${kind}:${id}`

/**
 * @param installable Kind and identifier of the installable
 * @description Returns the identifier of the installable.
 */
export const installableId = ([, id]: Installable): InstallableId => id

/**
 * @param installable Kind and identifier of the installable
 * @description Returns the kind and the identifier of the installable as one label.
 */
export const formatInstallable = ([kind, id]: Installable): string => `${kind} "${id}"`
