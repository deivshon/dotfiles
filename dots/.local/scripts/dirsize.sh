#!/bin/sh

REQUESTED_DIR="$1"

[ -z "$REQUESTED_DIR" ] && printf 1>&2 "Provide a directory\n" && exit 1
[ -e "$REQUESTED_DIR" ] || { printf 1>&2 "%s does not exist\n" "$REQUESTED_DIR"; exit 1; }
[ -d "$REQUESTED_DIR" ] || { printf 1>&2 "%s does not seem to be a directory\n" "$REQUESTED_DIR"; exit 1; }

du -h "$REQUESTED_DIR" | tail -n1
