#!/bin/sh

systemctl --user import-environment DISPLAY
eval "$(ssh-agent)"

start_dwm() {
    dunst -config ~/.config/dunst/dunstrc-dwm &
    plstatus &
    feh --bg-fill <sub<xwms-wallpaper-path>> &
    ~/.startup/dwm/startops.sh &
    exec dwm
}

start_qtile() {
    export QTILE_WIDGETS_CACHE_DIR="/tmp/qtile-configs-cache"
    export QTILE_UPDATES_CACHE_FILE="arch-updates-checker"

    dunst -config ~/.config/dunst/dunstrc-qtile &
    arch-updates-checker "$QTILE_WIDGETS_CACHE_DIR/$QTILE_UPDATES_CACHE_FILE" 60 &
    ~/.startup/qtile/startops.sh && exec qtile start
}

nm-applet &
polkit-dumb-agent &
xset -b &
case $1 in
    dwm  ) start_dwm;;
    qtile) start_qtile;;
esac
