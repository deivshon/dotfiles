import { existsSync } from "node:fs"
import { homedir } from "node:os"
import path from "node:path"
import { argv, cwd } from "node:process"

import { FILES_DIRECTORY, HOME_PATH_PREFIX } from "../consts"
import { applications } from "../data"
import type { Application } from "../types/applications/applications"
import type {
    ConfigFile,
    Configs,
    ConfigTarget,
    ConfigTargetBase,
} from "../types/configs"
import type { Installable } from "../types/installables"
import type { Platform } from "../types/platforms"
import { isConfigCurrent } from "./configs"

/**
 * @param start Directory where the search begins
 * @description Returns the first directory of the parent chain that holds the files directory.
 */
const findRepositoryRoot = (start: string): string => {
    const parent = path.dirname(start)
    return existsSync(path.join(start, FILES_DIRECTORY)) || parent === start
        ? start
        : findRepositoryRoot(parent)
}

/** @remarks The bundle runs from a directory of the repository, so the search starts there. */
export const repositoryRoot = findRepositoryRoot(path.dirname(argv[1] ?? cwd()))

/**
 * @param segments Segments of the path
 * @description Returns the segments with the home prefix replaced by the home directory.
 */
const expandHome = (segments: string[]): string[] =>
    segments[0] === HOME_PATH_PREFIX ? [homedir(), ...segments.slice(1)] : segments

/**
 * @param configs Config files of one application
 * @param platform Target operating system
 * @description Returns the config files that the platform covers.
 */
const configsOfPlatform = (configs: Configs, platform: Platform): ConfigFile[] =>
    Array.isArray(configs) ? configs : configs[platform]

/**
 * @param application Application of the config files
 * @param platform Target operating system
 * @description True when the application exists on the platform.
 */
const coversPlatform = (application: Application, platform: Platform): boolean =>
    "instances" in application
        ? application.instances[platform] !== null
        : application.platform === platform

/**
 * @param installable Kind and identifier of the application
 * @param config Config file of the application
 * @description Builds the target of one config file, and reads the state of its destination.
 */
const resolveTarget = async (
    installable: Installable,
    config: ConfigFile,
): Promise<ConfigTarget> => {
    const base: ConfigTargetBase = {
        type: config.type,
        source: path.resolve(repositoryRoot, ...config.source),
        destination: path.join(...expandHome(config.destination)),
    }
    const skip = await isConfigCurrent(base)

    return {
        type: base.type,
        source: base.source,
        destination: base.destination,
        installable,
        skip,
    }
}

/**
 * @param platform Target operating system
 * @description Builds the target of every config file of the platform.
 * @remarks Leaves out the applications that the platform does not cover.
 */
export const buildConfigPlan = (platform: Platform): Promise<ConfigTarget[]> =>
    Promise.all(
        Object.values(applications)
            .filter(application => coversPlatform(application, platform))
            .flatMap(application =>
                configsOfPlatform(application.configs, platform).map(config =>
                    resolveTarget(["application", application.id], config),
                ),
            ),
    )
