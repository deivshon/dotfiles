#!/bin/sh

sudo pacman -Syu && yay -Sua
EXIT_CODE=$?

[ "$EXIT_CODE" != 0 ] && exit "$EXIT_CODE"

rm -f /tmp/command-cache/a4f5ffa84acbb597099ede9dca88e43b

[ "$QTILE_UPDATES_CHECKER_PID" = "" ] && exit 0
kill -USR1 "$QTILE_UPDATES_CHECKER_PID"
