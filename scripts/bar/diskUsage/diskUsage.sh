#!/bin/sh

while IFS= read -r line; do
    currentCol=$(printf "%s" "$line" | awk '{print $6}')
    if [ "$currentCol" = "/" ]; then
        printf "%s" "$line" | awk '{printf $4}'
        printf "|"
        exit
    fi
done << EOF
$(df -h)
EOF
