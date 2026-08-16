import { homedir } from "node:os"
import path from "node:path"

export const PACMAN_EXECUTABLE = "pacman"
export const PARU_EXECUTABLE = "paru"
export const MAKEPKG_EXECUTABLE = "makepkg"
export const GIT_EXECUTABLE = "git"
export const CURL_EXECUTABLE = "curl"
export const BREW_EXECUTABLE = "brew"
export const WINGET_EXECUTABLE = "winget"
export const SUDO_EXECUTABLE = "sudo"
export const BASH_EXECUTABLE = "bash"
export const RUSTUP_EXECUTABLE = "rustup"
export const VS_CODE_EXECUTABLE = "code"
export const CARGO_EXECUTABLE = "cargo"
export const CLAUDE_CODE_EXECUTABLE = "claude"

export const CLAUDE_CODE_INSTALL_SCRIPT_URL = "https://claude.ai/install.sh"

export const WHICH_EXECUTABLE = "which"
export const WHERE_EXECUTABLE = "where"

export const FALLBACK_EDITOR = "vi"

export const TEMPORARY_DIRECTORY_PREFIX = "dotfiles-"
export const INSTALL_SCRIPT_FILE_NAME = "install.sh"

export const LOCAL_BIN_DIRECTORY = path.join(homedir(), ".local", "bin")

/** @remarks Owner reads, writes, and runs the file. Everyone else reads it and runs it. */
export const EXECUTABLE_FILE_MODE = 0o755
