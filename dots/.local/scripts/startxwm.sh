#!/bin/sh

start_dwm() {
    dunst &
    plstatus &
    feh --bg-fill <sub<xwms-wallpaper-path>> &
    ~/.startup/dwm/startops.sh && exec dwm
}

systemctl --user import-environment DISPLAY

nm-applet &
polkit-gnome-authentication-agent-1 &
xset -b &
case $1 in
    dwm  ) start_dwm;;
esac

printf 1>&2 "%s is not a valid startxwm option" $1
