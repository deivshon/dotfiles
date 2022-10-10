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

dwm_download() {
    if ! [ -d ~/.config/dwm ]; then
        git clone https://github.com/deivshon/dwm-flexipatch ~/.config/dwm
    else
        printf "%sdwm: ~/.config/dwm already exists, pulling%s\n" "${red}" "${normal}"
        git -C ~/.config/dwm pull
    fi
}

slstatus_download() {
    if ! [ -d ~/.config/slstatus ]; then
        git clone https://github.com/deivshon/slstatus ~/.config/slstatus/
    else
        printf "%sslstatus: ~/.config/slstatus already exists, pulling%s\n" "${red}" "${normal}"
        git -C ~/.config/slstatus pull
    fi    
}

yay_download() {
    if ! [ -d ~/yay ]; then
        git clone https://aur.archlinux.org/yay.git ~/yay
    else
        printf "%syay: ~/yay already exists%s\n" "${red}" "${normal}"
    fi
}

st_download() {
    if ! [ -d ~/.config/st ]; then
        git clone https://github.com/deivshon/st ~/.config/st
    else
        printf "%sst: ~/.config/st already exists, pulling%s\n" "${red}" "${normal}"
        git -C ~/.config/st pull
    fi
}

change_vol_pactl_download() {
    if ! [ -d ~/.config/change-vol-pactl ]; then
        git clone https://github.com/deivshon/change-vol-pactl ~/.config/change-vol-pactl
    else
        printf "%schange-vol-pactl: ~/.config/change-vol-pactl already exists, pulling%s\n" "${red}" "${normal}"
        git -C ~/.config/change-vol-pactl pull
    fi
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
