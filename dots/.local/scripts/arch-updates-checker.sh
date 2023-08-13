#!/bin/sh

is_number() {
    expr "$1" : '^[0-9]*$' > /dev/null
}

log_err() {
    >&2 echo "$(date +'[%Y-%m-%d %H:%M:%S] !')" "$1"
}

log_info() {
    echo "$(date +'[%Y-%m-%d %H:%M:%S] -')" "$1"
}

cache() {
    DIRNAME=$(dirname "$2")

    [ ! -d "$DIRNAME" ] && mkdir -p "$DIRNAME"
    echo "$1" > "$2"
}

CACHE_FILE=""
if [ "$1" != "" ]; then
    CACHE_FILE="$1"

    cache 0 "$CACHE_FILE"
fi

SLEEP_TIME=60
if [ "$2" != "" ]; then
    if ! is_number "$2"; then
        log_err "sleep time '$2' is not a number"
        exit 1
    else
        SLEEP_TIME=$2
    fi
elif [ "$CACHE_FILE" != "" ]; then
    log_info "using default period (60s)"
fi

while true; do
    PACMAN_UPDATES=$(checkupdates)
    CHECKUPDATES_STATUS=$?
    PACMAN_UPDATES_NUMBER=0

    YAY_UPDATES=$(yay -Qua)
    YAY_STATUS=$?
    YAY_UPDATES_NUMBER=0

    ERROR_OCCURRED=0

    if [ "$CHECKUPDATES_STATUS" = 2 ]; then
        PACMAN_UPDATES_NUMBER=0
    elif [ "$CHECKUPDATES_STATUS" = 0 ]; then
        PACMAN_UPDATES_NUMBER=$(echo "$PACMAN_UPDATES" | wc -l)
    else
        log_err "checkupdates returned an error code: $CHECKUPDATES_STATUS"
        ERROR_OCCURRED=1
    fi

    if [ "$YAY_STATUS" = 1 ]; then
        YAY_UPDATES_NUMBER=0
    elif [ "$YAY_STATUS" = 0 ]; then
        YAY_UPDATES_NUMBER=$(echo "$YAY_UPDATES" | wc -l)
    else
        log_err "yay returned an error code: $YAY_STATUS"
        ERROR_OCCURRED=1
    fi

    if [ "$ERROR_OCCURRED" != 1 ]; then
        TOTAL_UPDATES=$((PACMAN_UPDATES_NUMBER + YAY_UPDATES_NUMBER))
        if [ "$CACHE_FILE" = "" ]; then
            echo "$TOTAL_UPDATES"
            exit 0
        else
            cache "$TOTAL_UPDATES" "$CACHE_FILE"
            log_info "cached latest result: $TOTAL_UPDATES"
        fi
    elif [ "$CACHE_FILE" = "" ]; then
        exit 1
    fi

    sleep "$SLEEP_TIME"
done
