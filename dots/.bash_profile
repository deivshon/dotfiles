#!/bin/bash

source ~/.bash_profile_device

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

export EDITOR=nano

PATH=${PATH}:~/.local/scripts/:

if [ -z "$DISPLAY" ]; then
    case $(tty) in
        /dev/tty1)
            Hyprland
            ;;
        /dev/tty2)
            startx
            ;;
    esac
fi
