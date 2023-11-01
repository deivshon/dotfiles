#!/bin/sh

start_dwm() {
    dunst &
    plstatus &
    feh --bg-fill <sub<xwms-wallpaper-path>> &
    ~/.startup/dwm/startops.sh && exec dwm
}

start_qtile() {
    dunst &
    ~/.startup/qtile/startops.sh && exec qtile start
}

systemctl --user import-environment DISPLAY

nm-applet &
polkit-gnome-authentication-agent-1 &
xset -b &
case $1 in
    dwm  ) start_dwm;;
    qtile) start_qtile;;
esac
