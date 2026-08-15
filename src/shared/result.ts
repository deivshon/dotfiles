export interface Ok<T> {
    success: true
    value: T
}

export interface Err<E> {
    success: false
    error: E
}

export type Result<T, E> = Ok<T> | Err<E>

/**
 * @template T Type of the value
 * @param value Value to wrap
 * @description Builds a successful result.
 */
const ok = <T>(value: T): Ok<T> => ({ success: true, value })

/**
 * @template E Type of the error
 * @param error Error to wrap
 * @description Builds a failed result.
 */
const err = <E>(error: E): Err<E> => ({ success: false, error })

/**
 * @template T Type of the value
 * @template E Type of the error
 * @param run Function to run
 * @param onThrow Maps the thrown value to an error
 * @description Runs a function that can throw and returns its outcome as a result.
 */
const trySync = <T, E>(run: () => T, onThrow: (cause: unknown) => E): Result<T, E> => {
    try {
        return ok(run())
    } catch (error) {
        return err(onThrow(error))
    }
}

/**
 * @template T Type of the value
 * @template E Type of the error
 * @param run Function that returns the promise
 * @param onThrow Maps the rejection value to an error
 * @description Awaits a promise that can reject and returns its outcome as a result.
 */
const tryAsync = async <T, E>(
    run: () => Promise<T>,
    onThrow: (cause: unknown) => E,
): Promise<Result<T, E>> => {
    try {
        return ok(await run())
    } catch (error) {
        return err(onThrow(error))
    }
}

/**
 * @template T Type of the source value
 * @template U Type of the mapped value
 * @param mapValue Maps the value
 * @description Maps the value of a successful result.
 */
const map =
    <T, U>(mapValue: (value: T) => U) =>
    <E>(result: Result<T, E>): Result<U, E> =>
        result.success ? ok(mapValue(result.value)) : result

/**
 * @template E Type of the source error
 * @template F Type of the mapped error
 * @param mapError Maps the error
 * @description Maps the error of a failed result.
 */
const mapErr =
    <E, F>(mapError: (error: E) => F) =>
    <T>(result: Result<T, E>): Result<T, F> =>
        result.success ? result : err(mapError(result.error))

/**
 * @template T Type of the source value
 * @template U Type of the next value
 * @template F Type of the next error
 * @param next Maps the value to the next result
 * @description Chains an operation that can fail onto a successful result.
 */
const bind =
    <T, U, F>(next: (value: T) => Result<U, F>) =>
    <E>(result: Result<T, E>): Result<U, E | F> =>
        result.success ? next(result.value) : result

/**
 * @template T Type of the value
 * @param fallback Value returned when the result is failed
 * @description Returns the value of a successful result, or the fallback.
 */
const unwrapOr =
    <T>(fallback: T) =>
    <E>(result: Result<T, E>): T =>
        result.success ? result.value : fallback

/**
 * @template T Type of the values
 * @template E Type of the errors
 * @param results Results to collect
 * @description Returns the values of every result, or the first error.
 */
const sequence = <T, E>(results: Array<Result<T, E>>): Result<T[], E> =>
    results.find(result => !result.success) ??
    ok(results.flatMap(result => (result.success ? [result.value] : [])))

export const Result = {
    ok,
    err,
    try: trySync,
    tryAsync,
    map,
    mapErr,
    bind,
    unwrapOr,
    sequence,
}
