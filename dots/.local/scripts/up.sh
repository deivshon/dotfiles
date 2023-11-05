#!/bin/sh

paru -Syu
EXIT_CODE=$?

rm -rf /tmp/command-cache/aus/

exit "$EXIT_CODE"
