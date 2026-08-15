import { exit, platform as operatingSystem } from "node:process"

import { colors } from "es-toolkit/server"
import { match } from "ts-pattern"

import type { Platform } from "../types/platforms"

/**
 * @description Returns the platform of the current operating system.
 * @remarks Ends the process when the operating system has no platform.
 */
const getPlatform = (): Platform =>
    match(operatingSystem)
        .returnType<Platform>()
        .with("linux", () => "arch-linux")
        .with("darwin", () => "mac-os")
        .with("win32", () => "windows")
        .otherwise(() => {
            console.error(colors.red(`Unsupported operating system: ${operatingSystem}`))
            return exit(1)
        })

export const platform = getPlatform()
