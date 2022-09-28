#!/bin/sh

cyan=$(tput setaf 6 bold)
red=$(tput setaf 1 bold)
green=$(tput setaf 2 bold)
normal=$(tput sgr0)

dwm_slstatus_downloads() {
    printf "%sStarting downloads%s\n" "${green}" "${normal}"

    # Install/Update dwm-flexipatch
    if ! [ -d ~/.config/dwm ]; then
        printf "%sStarting dwm-flexipatch download%s\n" "${cyan}" "${normal}"
        git clone https://github.com/deivshon/dwm-flexipatch ~/.config/dwm
    else
        printf "%sdwm-flexipatch: ~/.config/dwm-flexipatch already exists, pulling%s\n" "${red}" "${normal}"
        cd ~/.config/dwm || exit
        git pull
        cd ~ || exit
    fi

    # Install/Update slstatus
    if ! [ -d ~/.config/slstatus ]; then
        printf "%sStarting slstatus download%s\n" "${cyan}" "${normal}"
        git clone https://github.com/deivshon/slstatus ~/.config/slstatus/
    else
        printf "%sslstatus: ~/.config/slstatus already exists, pulling%s\n" "${red}" "${normal}"
        cd ~/.config/slstatus || exit
        git pull
        cd ~ || exit
    fi    

    printf "%sDownloads over, exiting%s\n" "${green}" "${normal}"
}

dwm_slstatus_compilations() {
    printf "%sStarting compilations%s\n" "${green}" "${normal}"

    # dwm-flexipatch compilation
    cd ~/.config/dwm || exit
    printf "%sStarting dwm-flexipatch compilation%s\n" "${cyan}" "${normal}"
    sudo make clean install

    # slstatus compilation
    cd ~/.config/slstatus || exit
    printf "%sStarting slstatus compilation%s\n" "${cyan}" "${normal}"
    sudo make clean install

    printf "%sCompilations over, exiting%s\n" "${green}" "${normal}"
}

yay_install() {
    cd ~ || exit
    if ! [ -d ~/yay ]; then
        git clone https://aur.archlinux.org/yay.git
        cd yay || exit
        makepkg -si
    else
        printf "%syay: ~/yay already exists%s\n" "${red}" "${normal}"
    fi
}

if [ "$1" = "-d" ]; then
    dwm_slstatus_downloads
elif [ "$1" = "-c" ]; then
    dwm_slstatus_compilations
elif [ "$1" = "-y" ]; then
    yay_install
else
    echo "Provide an acceptable argument:
        -d -> perform dwm and slstatus downloads
        -c -> perform dwm and slstatus compilations
        -y -> perform yay installation"
fi
