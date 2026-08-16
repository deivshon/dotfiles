import type { Installable } from "./installables"
import type { Platform } from "./platforms"

export type FileCopyType = "file-copy"
export type JsonMergeType = "json-merge"

export type ConfigType = FileCopyType | JsonMergeType

export interface FileCopyConfig {
    type: FileCopyType
    source: string[]
    destination: string[]
}

export interface JsonMergeConfig {
    type: JsonMergeType
    source: string[]
    destination: string[]
}

export type ConfigFile = FileCopyConfig | JsonMergeConfig

export type Configs = ConfigFile[] | Record<Platform, ConfigFile[]>

export interface ConfigTargetBase {
    type: ConfigType
    source: string
    destination: string
}

export interface ConfigTarget extends ConfigTargetBase {
    installable: Installable
    skip: boolean
}

export type ConfigStatus = "copied" | "replaced" | "unchanged"

export interface ConfigResult {
    target: ConfigTarget
    status: ConfigStatus
    backupPath: string | null
}
