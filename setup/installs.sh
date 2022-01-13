#!/bin/sh

cyan=$(tput setaf 6 bold)
red=$(tput setaf 1 bold)
green=$(tput setaf 2 bold)
normal=$(tput sgr0)

downloads() {
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

compilations() {
    printf "Starting compilations%s\n" "${green}" "${normal}"

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

if [ "$1" = "-d" ]; then
    downloads
elif [ "$1" = "-c" ]; then
    compilations
else
    echo "Provide an acceptable argument:
        -d -> perform downloads
        -c -> perform compilations"
fi
