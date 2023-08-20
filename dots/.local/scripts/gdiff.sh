#!/bin/sh

COMMIT_NUMBER="1"
if [ "$1" != "" ]; then
    COMMIT_NUMBER="$1"
fi

TOTAL_COMMITS="$(git --no-pager log --oneline | wc -l)"
if [ "${COMMIT_NUMBER}" -ge "${TOTAL_COMMITS}" ]; then
    TOTAL_COMMITS="$(echo "${TOTAL_COMMITS}" 1 - p | dc)"
    printf "Wrong commit number, oldest commit: %s\n" "${TOTAL_COMMITS}"
    return
fi

COMMIT="$(git --no-pager log --oneline | awk "FNR == ${COMMIT_NUMBER} {print \$1}")"
git --no-pager diff --color=always "${COMMIT}"~ "${COMMIT}" | less -r
