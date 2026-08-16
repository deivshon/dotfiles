export type UserApplicationId =
    | "git"
    | "paru"
    | "brew"
    | "ghostty"
    | "sudo"
    | "eza"
    | "ranger"
    | "wget"
    | "firefox"
    | "tmux"
    | "btop"
    | "rustup"
    | "bat"
    | "doas"
    | "dash"
    | "fish"
    | "go"
    | "tldr"
    | "hyprland"
    | "zed"
    | "pfetch-rs"
    | "visual-studio-code"
    | "ccommit"
    | "claude-code"

export type ArchLinuxSystemApplicationId = "pacman" | "makepkg"
export type MacOsSystemApplicationId = "curl"
export type WindowsSystemApplicationId = "winget"
export type SystemApplicationId =
    | ArchLinuxSystemApplicationId
    | MacOsSystemApplicationId
    | WindowsSystemApplicationId

export type ApplicationId = UserApplicationId | SystemApplicationId
