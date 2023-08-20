#!/bin/fish

set -U fish_greeting

set FISH_ALIASES_FILE "$HOME/.config/aliases/fish_aliases.fish"
if test -f "$FISH_ALIASES_FILE"
    source "$FISH_ALIASES_FILE"
else
    printf "Error: aliases file not found at $FISH_ALIASES_FILE" 1>&2
end
set -e FISH_ALIASES_FILE

function ssh-start
    eval (ssh-agent -c)

    for KEY in ~/.ssh/*
        if test -f "$KEY"
            set FILE_RESULT (file -b "$KEY")
            if string match -q "private key" "$FILE_RESULT"
                ssh-add "$KEY"
            end
        end
    end
end

if test "$TERM" = "foot"
    alias ssh "TERM=linux ssh"
    alias vagrant "TERM=linux vagrant"
end

afetch
