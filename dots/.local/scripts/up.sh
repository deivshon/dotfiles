#!/bin/sh

sudo pacman -Syu && paru -Sua
EXIT_CODE=$?

rm -rf /tmp/command-cache/aus/

[ "$EXIT_CODE" != 0 ] && exit "$EXIT_CODE"
