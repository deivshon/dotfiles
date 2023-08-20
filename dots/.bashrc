#!/bin/bash

[[ $- != *i* ]] && return

source ~/.bashrc_device

BASH_ALIASES_FILE="$HOME/.config/aliases/bash_aliases.bash"
if [ -f "$BASH_ALIASES_FILE" ]; then
    source "$BASH_ALIASES_FILE"
else
    printf "Error: aliases file not found at $BASH_ALIASES_FILE\n" 1>&2
fi
unset BASH_ALIASES_FILE

[ -r /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion

git_current_branch() {
    git branch 2> /dev/null | sed -e "/^[^*]/d" -e "s/* \(.*\)/ (\1)/"
}

if [[ ${EUID} == 0 ]]; then
    PS1="\[\e[01;31m\][\h\[\e[01;36m\] \W\[\e[01;31m\]]\$\[\e[00m\] "
else
    PS1="\[\e[01;32m\][\u@\h\[\e[01;37m\] \W\[\e[1;33m\]\$(git_current_branch)\[\e[01;32m\]]\$\[\e[00m\] "
fi

export HISTCONTROL=ignoredups:erasedups
shopt -s histappend

ssh-start() {
    eval "$(ssh-agent)"

    for KEY in ~/.ssh/*; do
        if [ -f "$KEY" ]; then
            FILE_RESULT=$(file -b "$KEY")
            if printf "%s" "$FILE_RESULT" | grep -q "private key"; then
                ssh-add "$KEY"
            fi
        fi
    done
}

[ "${TERM}" == "foot" ] && alias ssh="TERM=linux ssh" && alias vagrant="TERM=linux vagrant"

afetch
