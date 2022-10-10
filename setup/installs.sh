#!/bin/sh

cyan=$(tput setaf 6 bold)
red=$(tput setaf 1 bold)
green=$(tput setaf 2 bold)
normal=$(tput sgr0)

usage() {
    echo "Accepted first arguments (programs):
    yay
    dwm
    slstatus
    change_pactl_volume
    st

Accepted second arguments (actions):
    d -> download
    c -> compilation
    i -> download and compilation"
}

action_choice() {
    if [ "$2" = "d" ]; then
        printf "%sStarting $1 download%s\n" "${green}" "${normal}"

        "$1"_download && printf "%sEnded $1 download%s\n" "${green}" "${normal}"
    elif [ "$2" = "c" ]; then
        printf "%sStarting $1 compilation%s\n" "${green}" "${normal}"

        "$1"_compilation && printf "%sEnded $1 compilation%s\n" "${green}" "${normal}"
    elif [ "$2" = "i" ]; then
        printf "%sStarting $1 installation%s\n" "${green}" "${normal}"

        "$1"_download && "$1"_compilation && printf "%sEnded $1 installation%s\n" "${green}" "${normal}"
    else
        usage
    fi
}

########## Downloads ##########

# $1 -> Path to clone to
# $2 -> Repository link
# $3 -> Software name
git_download() {
    if ! [ -d "$1" ]; then
        git clone "$2" "$1"
    else
        printf "%s$3: $1 already exists, pulling%s\n" "${red}" "${normal}"
        git -C ~/.config/dwm pull
    fi
}

dwm_download() {
    git_download ~/.config/dwm https://github.com/deivshon/dwm-flexipatch dwm
}

slstatus_download() {
    git_download ~/.config/slstatus https://github.com/deivshon/slstatus slstatus
}

yay_download() {
    if ! [ -d ~/yay ]; then
        git clone https://aur.archlinux.org/yay.git ~/yay
    else
        printf "%syay: ~/yay already exists%s\n" "${red}" "${normal}"
    fi
}

st_download() {
    git_download ~/.config/st https://github.com/deivshon/st st
}

change_vol_pactl_download() {
    git_download ~/.config/change-vol-pactl https://github.com/deivshon/change-vol-pactl change_vol_pactl
}

########## Compilations ##########

dwm_compilation() {
    sudo make -C ~/.config/dwm clean install
}

slstatus_compilation() {
    sudo make -C ~/.config/slstatus clean install
}

yay_compilation() {
    if [ -d ~/yay ]; then
        cd ~/yay || exit
        makepkg -si
    else
        printf "%syay: ~/yay does not exist%s\n" "${red}" "${normal}"
    fi
}

st_compilation() {
    sudo make -C ~/.config/st clean install
}

change_vol_pactl_compilation() {
    sudo make -C ~/.config/change-vol-pactl clean install
}

########## Main ##########

action_choice "$1" "$2"
