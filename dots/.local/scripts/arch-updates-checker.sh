#!/bin/sh

LAST_SIGUSR1=0

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

run_and_cache() {
    CACHE_FILE="$1"
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
}

handle_sigusr1() {
    CACHE_FILE="$1"
    LAST_SIGUSR1=1
    run_and_cache "$CACHE_FILE"
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

trap 'handle_sigusr1 "$CACHE_FILE"' USR1

while true; do
    [ "$LAST_SIGUSR1" -eq 0 ] && run_and_cache "$CACHE_FILE"
    LAST_SIGUSR1=0

    sleep "$SLEEP_TIME" &
    wait $!
done
