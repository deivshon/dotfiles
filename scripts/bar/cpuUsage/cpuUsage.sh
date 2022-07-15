#!/bin/sh

suffix=""
if [ "$1" = "--separator" ]; then
    suffix="|"
fi

# $2 -> usr
# $4 -> sys
# $8 -> idle
usage=$(top -bn1 | grep '%Cpu' | awk '{cpuUsage=($2+$4)/($2+$4+$8)*100} END {print cpuUsage}')

printf "CPU %.1f%%%s" "$usage" "$suffix"
