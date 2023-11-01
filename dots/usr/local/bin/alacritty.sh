#!/bin/sh

/usr/bin/alacritty msg create-window $@ || exec /usr/bin/alacritty $@
