#!/bin/sh

downloads() {
    echo "Starting downloads"

    # Install dwm-flexipatch
    if ! [ -d ~/.config/dwm-flexipatch ]; then
        git clone https://github.com/bakkeby/dwm-flexipatch ~/.config/dwm-flexipatch/
    else
        echo "dwm-flexipatch: ~/.config/dwm-flexipatch already exists"
    fi

    # Install slstatus
    if ! [ -d ~/.config/slstatus ]; then
        git clone https://github.com/drkhsh/slstatus ~/.config/slstatus/
    else
        echo "slstatus: ~/.config/slstatus already exists"
    fi    

    echo "Downloads over, exiting"
}

compilations() {
    echo "Starting compilations"

    # dwm-flexipatch compilation
    cd ~/.config/dwm-flexipatch || exit
    echo "Starting dwm-flexipatch compilation"
    sudo make clean install

    # slstatus compilation
    cd ~/.config/slstatus || exit
    echo "Starting slstatus compilation"
    sudo make clean install

    echo "Compilations over, exiting"
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
