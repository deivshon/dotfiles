#!/bin/sh

dir_count=0
for _ in "$@"; do
    dir_count=$((dir_count + 1))
done

for requested_dir in "$@"; do
    [ -z "$requested_dir" ] && {
        [ $dir_count -eq 1 ] && printf 1>&2 "Received empty directory\n"
        continue
    }
    [ -e "$requested_dir" ] || {
        [ $dir_count -eq 1 ] && printf 1>&2 "%s does not exist\n" "$requested_dir"
        continue
    }
    [ -d "$requested_dir" ] || {
        [ $dir_count -eq 1 ] && printf 1>&2 "%s does not seem to be a directory\n" "$requested_dir"
        continue
    }

    du -h "$requested_dir" | tail -n1
done
