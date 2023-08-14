#!/bin/sh

sudo pacman -Syu && yay -Sua
EXIT_CODE=$?

[ "$EXIT_CODE" != 0 ] && exit "$EXIT_CODE"
[ "$QTILE_UPDATES_CHECKER_PID" = "" ] && exit 0

kill -USR1 "$QTILE_UPDATES_CHECKER_PID"
