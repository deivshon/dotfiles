#!/bin/bash

source ~/.bash_profile_device

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

export SHELL=/bin/fish
export EDITOR=nano

export PF_SOURCE=~/.config/pfetch/pfetch-config.sh

PATH=${PATH}:~/.local/scripts:~/.local/bin

launch_hyprland() {
    Hyprland
}

launch_dwm() {
    startx dwm
}

launch_qtile() {
    startx qtile
}

launch_wm() {
    launch_"$1"
}

if [ -z "$DISPLAY" ]; then
    case $(tty) in
        /dev/tty1) launch_wm "$TTY1_WM";;
        /dev/tty2) launch_wm "$TTY2_WM";;
        /dev/tty3) launch_wm "$TTY3_WM";;
    esac
fi
