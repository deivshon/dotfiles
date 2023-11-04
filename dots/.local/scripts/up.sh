#!/bin/sh

pikaur -Syu
EXIT_CODE=$?

rm -rf /tmp/command-cache/aus/

exit "$EXIT_CODE"
