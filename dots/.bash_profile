#!/bin/bash

source ~/.bash_profile_device

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export SHELL=/bin/fish
export EDITOR=nano

PATH=${PATH}:/usr/lib/polkit-gnome/:~/.local/scripts:~/.local/bin

launch_hyprland() {
    Hyprland
}

launch_dwm() {
    startx dwm
}

if [ -z "$DISPLAY" ]; then
    case $(tty) in
        /dev/tty1) launch_"$TTY1_WM";;
        /dev/tty2) launch_"$TTY2_WM";;
    esac
fi
