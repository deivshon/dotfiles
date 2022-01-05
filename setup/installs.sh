#!/bin/sh

cyan=$(tput setaf 6 bold)
red=$(tput setaf 1 bold)
green=$(tput setaf 2 bold)
normal=$(tput sgr0)

downloads() {
    printf "%sStarting downloads%s\n" "${green}" "${normal}"

    # Install dwm-flexipatch
    if ! [ -d ~/.config/dwm-flexipatch ]; then
        printf "%sStarting dwm-flexipatch download%s\n" "${cyan}" "${normal}"
        git clone https://github.com/bakkeby/dwm-flexipatch ~/.config/dwm-flexipatch/
    else
        printf "%sdwm-flexipatch: ~/.config/dwm-flexipatch already exists%s\n" "${red}" "${normal}"
    fi

    # Install slstatus
    if ! [ -d ~/.config/slstatus ]; then
        printf "%sStarting slstatus download%s\n" "${cyan}" "${normal}"
        git clone https://github.com/drkhsh/slstatus ~/.config/slstatus/
    else
        printf "%sslstatus: ~/.config/slstatus already exists%s\n" "${red}" "${normal}"
    fi    

    printf "%sDownloads over, exiting%s\n" "${green}" "${normal}"
}

compilations() {
    printf "Starting compilations%s\n" "${green}" "${normal}"

    # dwm-flexipatch compilation
    cd ~/.config/dwm-flexipatch || exit
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
