#!/bin/sh

suffix=""
if [ "$1" = "--separator" ]; then
    suffix="|"
fi

while IFS= read -r line; do
    currentCol=$(printf "%s" "$line" | awk '{print $6}')
    if [ "$currentCol" = "/" ]; then
        printf "DISK "
        printf "%s" "$line" | awk '{printf $4}'
        printf "%s\n" "$suffix"
        exit
    fi
done << EOF
$(df -h)
EOF
