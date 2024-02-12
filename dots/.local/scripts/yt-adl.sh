#!/bin/sh

YOUTUBE_LINK=$1
MAX_SIZE="15"

[ -n "$2" ] && MAX_SIZE=$2

yt-dlp -o "%(title)s.%(ext)s" --format "bestaudio[filesize<=$MAX_SIZE M]" "$YOUTUBE_LINK" -x --audio-format mp3 --audio-quality 0 --sponsorblock-remove all
