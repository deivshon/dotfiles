#!/bin/sh

# $2 -> usr
# $4 -> sys
# $8 -> idle
usage=$(top -bn1 | grep '%Cpu' | awk '{cpuUsage=($2+$4)/($2+$4+$8)*100} END {print cpuUsage}')

printf "%.1f%%" "$usage"
