#!/bin/sh

i3lock \
    --ring-width=15 \
    --clock \
    --time-str=%R \
    --date-str="%A %e of %B" \
    --radius=250 \
    --blur=1 \
    --indicator \
    --inside-color=<sub<i3l--inside-color>> \
    --insidever-color=<sub<i3l--inside-ver-color>> \
    --insidewrong-color=<sub<i3l--inside-wrong-color>> \
    --keyhl-color=<sub<i3l--key-hl-color>> \
    --bshl-color=<sub<i3l--bs-hl-color>> \
    --separator-color=<sub<i3l--separator-color>> \
    --line-color=<sub<i3l--line-color>> \
    --line-uses-ring \
    --time-color=<sub<i3l--text-color>> \
    --date-color=<sub<i3l--text-color>> \
    --greeter-color=<sub<i3l--text-color>> \
    --modif-color=<sub<i3l--text-color>> \
    --wrong-color=<sub<i3l--text-wrong-color>> \
    --verif-color=<sub<i3l--text-ver-color>> \
    --date-size=30 \
    --time-size=60 \
    --ring-color=<sub<i3l--ring-color>> \
    --ringver-color=<sub<i3l--ring-ver-color>> \
    --ringwrong-color=<sub<i3l--ring-wrong-color>>
