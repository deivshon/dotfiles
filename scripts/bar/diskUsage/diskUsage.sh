#!/bin/sh

while IFS= read -r line; do
    currentCol=$(printf "%s" "$line" | awk '{print $6}')
    if [ "$currentCol" = "/" ]; then
        printf "%s" "$line" | awk '{print $4}'
    fi
done << EOF
$(df -h)
EOF
