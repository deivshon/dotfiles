#!/bin/sh

systemctl --user import-environment DISPLAY
eval "$(ssh-agent)"

start_dwm() {
    plstatus &
    feh --bg-fill <sub<xwms-wallpaper-path>> &
    ~/.startup/dwm/startops.sh &
    exec dwm
}

start_qtile() {
    ~/.startup/qtile/startops.sh &
    exec qtile start
}

nm-applet &
polkit-dumb-agent &
dunst &
xset -b &
case $1 in
    dwm  ) start_dwm;;
    qtile) start_qtile;;
esac
