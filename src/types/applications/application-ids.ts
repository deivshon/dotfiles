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
    | "opendoas"
    | "dash"
    | "fish"
    | "go"
    | "tldr"
    | "hyprland"
    | "zed"
    | "pfetch-rs"
    | "visual-studio-code-bin"
    | "ccommit"

export type ArchLinuxSystemApplicationId = "pacman" | "makepkg"
export type MacOsSystemApplicationId = "curl"
export type WindowsSystemApplicationId = "winget"
export type SystemApplicationId =
    | ArchLinuxSystemApplicationId
    | MacOsSystemApplicationId
    | WindowsSystemApplicationId

export type ApplicationId = UserApplicationId | SystemApplicationId
