#!/bin/sh

memInfo=$(grep -e MemTotal -e MemAvailable < /proc/meminfo)

while IFS= read -r line; do
    if [ "$(printf "%s" "$line" | grep "MemTotal")" != "" ]; then
        memTot=$(printf "%s" "$line" | awk '{print $2}')
    else
        memAvail=$(printf "%s" "$line" | awk '{print $2}')
    fi
done << EOF
$memInfo
EOF

memPerc=$(echo "100 - ($memAvail / $memTot)*100" | bc -l)

memTot=$(echo "$memTot" / 1000000 | bc -l)
memAvail=$(echo "$memAvail" / 1000000 | bc -l)

memInUse=$(echo "$memTot - $memAvail" | bc -l)
printf "RAM %.2fG/%.2fG (%.1f%%)|\n" "$memInUse" "$memTot" "$memPerc"
