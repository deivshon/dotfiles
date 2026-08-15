/**
 * @template T Union to choose from
 * @template U Chosen member
 * @description Returns the chosen member of a union, and fails to compile when it leaves the union.
 */
export type Select<T, U extends T> = U

/**
 * @template T Union to reduce
 * @template U Members to remove
 * @description Returns the union without the excluded members.
 */
export type Exclude<T, U extends T> = T extends U ? never : T
