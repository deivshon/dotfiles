import path from "node:path"

import {
    CARGO_EXECUTABLE,
    CLAUDE_CODE_EXECUTABLE,
    CLAUDE_CODE_INSTALL_SCRIPT_URL,
    FILES_DIRECTORY,
    HOME_PATH_PREFIX,
    LOCAL_BIN_DIRECTORY,
} from "./consts"
import {
    archLinuxCustomInstall,
    archLinuxSystemApplication,
    brewCask,
    brewFormula,
    extension,
    fileCopy,
    jsonMerge,
    library,
    macOsCustomInstall,
    macOsSystemApplication,
    pacmanPackage,
    paruPackage,
    toolchain,
    userApplication,
    windowsSystemApplication,
} from "./installables/builders"
import {
    installArchLinuxPackageFromAurManual,
    installFromGit,
    installFromScript,
    installRustupToolchain,
    installVsCodeExtension,
} from "./installs/installs"
import {
    isExecutableInPath,
    isRustupToolchainInstalled,
    isVsCodeExtensionInstalled,
} from "./installs/verification"
import type {
    ApplicationId,
    SystemApplicationId,
    UserApplicationId,
} from "./types/applications/application-ids"
import type {
    Application,
    SystemApplication,
    UserApplication,
} from "./types/applications/applications"
import type { ExtensionId } from "./types/extensions/extension-ids"
import type { Extension } from "./types/extensions/extensions"
import type { Library } from "./types/libraries/libraries"
import type { LibraryId } from "./types/libraries/library-ids"
import type { ToolchainId } from "./types/toolchains/toolchain-ids"
import type { Toolchain } from "./types/toolchains/toolchains"

export const systemApplications: {
    [K in SystemApplicationId]: SystemApplication & { id: K }
} = {
    pacman: archLinuxSystemApplication("pacman"),
    makepkg: archLinuxSystemApplication("makepkg"),
    curl: macOsSystemApplication("curl"),
    winget: windowsSystemApplication("winget"),
}

export const userApplications: {
    [K in UserApplicationId]: UserApplication & { id: K }
} = {
    paru: userApplication("paru", {
        "arch-linux": archLinuxCustomInstall({
            install: installArchLinuxPackageFromAurManual(
                "https://aur.archlinux.org/paru.git",
            ),
            isInstalled: isExecutableInPath("paru"),
            requires: [
                ["application", "git"],
                ["application", "makepkg"],
                ["library", "base-devel"],
            ],
        }),
        "mac-os": null,
        windows: null,
    }),
    git: userApplication("git", {
        "arch-linux": pacmanPackage("git"),
        "mac-os": brewFormula("git"),
        windows: null,
    }),
    brew: userApplication("brew", {
        "arch-linux": null,
        "mac-os": macOsCustomInstall({
            install: installFromScript(
                "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh",
            ),
            isInstalled: isExecutableInPath("brew"),
            requires: [],
        }),
        windows: null,
    }),
    ghostty: userApplication(
        "ghostty",
        {
            "arch-linux": pacmanPackage("ghostty"),
            "mac-os": brewCask("ghostty"),
            windows: null,
        },
        [
            fileCopy(
                [FILES_DIRECTORY, "ghostty", "config.ghostty"],
                [HOME_PATH_PREFIX, ".config", "ghostty", "config.ghostty"],
            ),
        ],
    ),
    sudo: userApplication("sudo", {
        "arch-linux": pacmanPackage("sudo"),
        "mac-os": null,
        windows: null,
    }),
    eza: userApplication("eza", {
        "arch-linux": pacmanPackage("eza"),
        "mac-os": null,
        windows: null,
    }),
    ranger: userApplication("ranger", {
        "arch-linux": pacmanPackage("ranger"),
        "mac-os": null,
        windows: null,
    }),
    wget: userApplication("wget", {
        "arch-linux": pacmanPackage("wget"),
        "mac-os": null,
        windows: null,
    }),
    firefox: userApplication("firefox", {
        "arch-linux": pacmanPackage("firefox"),
        "mac-os": null,
        windows: null,
    }),
    tmux: userApplication("tmux", {
        "arch-linux": pacmanPackage("tmux"),
        "mac-os": null,
        windows: null,
    }),
    btop: userApplication("btop", {
        "arch-linux": pacmanPackage("btop"),
        "mac-os": null,
        windows: null,
    }),
    rustup: userApplication("rustup", {
        "arch-linux": pacmanPackage("rustup"),
        "mac-os": null,
        windows: null,
    }),
    bat: userApplication("bat", {
        "arch-linux": pacmanPackage("bat"),
        "mac-os": null,
        windows: null,
    }),
    doas: userApplication("doas", {
        "arch-linux": pacmanPackage("opendoas"),
        "mac-os": null,
        windows: null,
    }),
    dash: userApplication("dash", {
        "arch-linux": pacmanPackage("dash"),
        "mac-os": null,
        windows: null,
    }),
    fish: userApplication("fish", {
        "arch-linux": pacmanPackage("fish"),
        "mac-os": null,
        windows: null,
    }),
    go: userApplication("go", {
        "arch-linux": pacmanPackage("go"),
        "mac-os": null,
        windows: null,
    }),
    tldr: userApplication("tldr", {
        "arch-linux": pacmanPackage("tldr"),
        "mac-os": null,
        windows: null,
    }),
    hyprland: userApplication("hyprland", {
        "arch-linux": pacmanPackage("hyprland"),
        "mac-os": null,
        windows: null,
    }),
    zed: userApplication("zed", {
        "arch-linux": pacmanPackage("zed"),
        "mac-os": null,
        windows: null,
    }),
    "pfetch-rs": userApplication("pfetch-rs", {
        "arch-linux": pacmanPackage("pfetch-rs"),
        "mac-os": null,
        windows: null,
    }),
    "visual-studio-code": userApplication(
        "visual-studio-code",
        {
            "arch-linux": paruPackage("visual-studio-code-bin"),
            "mac-os": null,
            windows: null,
        },
        {
            "arch-linux": [
                jsonMerge(
                    [FILES_DIRECTORY, "vs-code", "settings.json"],
                    [HOME_PATH_PREFIX, ".config", "Code", "User", "settings.json"],
                ),
            ],
            "mac-os": [
                jsonMerge(
                    [FILES_DIRECTORY, "vs-code", "settings.json"],
                    [
                        HOME_PATH_PREFIX,
                        "Library",
                        "Application Support",
                        "Code",
                        "User",
                        "settings.json",
                    ],
                ),
            ],
            windows: [],
        },
    ),
    ccommit: userApplication("ccommit", {
        "arch-linux": archLinuxCustomInstall({
            install: installFromGit({
                repoUrl: "https://github.com/deivshon/ccommit.git",
                buildCommand: CARGO_EXECUTABLE,
                buildArgs: ["build", "--release", "--locked"],
                artifactPath: path.join("target", "release", "ccommit"),
                destinationPath: path.join(LOCAL_BIN_DIRECTORY, "ccommit"),
            }),
            isInstalled: isExecutableInPath("ccommit"),
            requires: [
                ["application", "git"],
                ["toolchain", "rust-stable"],
            ],
        }),
        "mac-os": null,
        windows: null,
    }),
    "claude-code": userApplication("claude-code", {
        "arch-linux": archLinuxCustomInstall({
            install: installFromScript(CLAUDE_CODE_INSTALL_SCRIPT_URL),
            isInstalled: isExecutableInPath(CLAUDE_CODE_EXECUTABLE),
            requires: [],
        }),
        "mac-os": macOsCustomInstall({
            install: installFromScript(CLAUDE_CODE_INSTALL_SCRIPT_URL),
            isInstalled: isExecutableInPath(CLAUDE_CODE_EXECUTABLE),
            requires: [],
        }),
        windows: null,
    }),
}

export const applications: { [K in ApplicationId]: Application & { id: K } } = {
    pacman: systemApplications.pacman,
    makepkg: systemApplications.makepkg,
    curl: systemApplications.curl,
    winget: systemApplications.winget,
    paru: userApplications.paru,
    git: userApplications.git,
    brew: userApplications.brew,
    ghostty: userApplications.ghostty,
    sudo: userApplications.sudo,
    eza: userApplications.eza,
    ranger: userApplications.ranger,
    wget: userApplications.wget,
    firefox: userApplications.firefox,
    tmux: userApplications.tmux,
    btop: userApplications.btop,
    rustup: userApplications.rustup,
    bat: userApplications.bat,
    doas: userApplications.doas,
    dash: userApplications.dash,
    fish: userApplications.fish,
    go: userApplications.go,
    tldr: userApplications.tldr,
    hyprland: userApplications.hyprland,
    zed: userApplications.zed,
    "pfetch-rs": userApplications["pfetch-rs"],
    "visual-studio-code": userApplications["visual-studio-code"],
    ccommit: userApplications.ccommit,
    "claude-code": userApplications["claude-code"],
}

export const libraries: { [K in LibraryId]: Library & { id: K } } = {
    "base-devel": library("base-devel", {
        "arch-linux": pacmanPackage("base-devel"),
        "mac-os": null,
        windows: null,
    }),
    "linux-headers": library("linux-headers", {
        "arch-linux": pacmanPackage("linux-headers"),
        "mac-os": null,
        windows: null,
    }),
    "bash-completion": library("bash-completion", {
        "arch-linux": pacmanPackage("bash-completion"),
        "mac-os": null,
        windows: null,
    }),
    "noto-fonts": library("noto-fonts", {
        "arch-linux": pacmanPackage("noto-fonts"),
        "mac-os": null,
        windows: null,
    }),
    "noto-fonts-cjk": library("noto-fonts-cjk", {
        "arch-linux": pacmanPackage("noto-fonts-cjk"),
        "mac-os": null,
        windows: null,
    }),
    "jetbrains-mono-nerd": library("jetbrains-mono-nerd", {
        "arch-linux": pacmanPackage("ttf-jetbrains-mono-nerd"),
        "mac-os": null,
        windows: null,
    }),
}

export const toolchains: { [K in ToolchainId]: Toolchain & { id: K } } = {
    "rust-stable": toolchain("rust-stable", {
        "arch-linux": archLinuxCustomInstall({
            install: installRustupToolchain("stable"),
            isInstalled: isRustupToolchainInstalled("stable"),
            requires: [["application", "rustup"]],
        }),
        "mac-os": null,
        windows: null,
    }),
    "rust-nightly": toolchain("rust-nightly", {
        "arch-linux": archLinuxCustomInstall({
            install: installRustupToolchain("nightly"),
            isInstalled: isRustupToolchainInstalled("nightly"),
            requires: [["application", "rustup"]],
        }),
        "mac-os": null,
        windows: null,
    }),
}

export const extensions: { [K in ExtensionId]: Extension & { id: K } } = {
    "oxc-vscode": extension("oxc-vscode", {
        "arch-linux": archLinuxCustomInstall({
            install: installVsCodeExtension("oxc.oxc-vscode"),
            isInstalled: isVsCodeExtensionInstalled("oxc.oxc-vscode"),
            requires: [["application", "visual-studio-code"]],
        }),
        "mac-os": null,
        windows: null,
    }),
}
