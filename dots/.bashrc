#!/bin/bash

[[ $- != *i* ]] && return

if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    Hyprland
fi

source ~/.bashrc_device

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
export HISTSIZE=100000
export HISTFILESIZE=100000
shopt -s histappend

extract() {
    if [ -f "$1" ] ; then
    case "$1" in
        *.tar.bz2)   tar xjf "$1"   ;;
        *.tar.gz)    tar xzf "$1"   ;;
        *.bz2)       bunzip2 "$1"   ;;
        *.rar)       unrar x "$1"   ;;
        *.gz)        gunzip "$1"    ;;
        *.tar)       tar xf "$1"    ;;
        *.tbz2)      tar xjf "$1"   ;;
        *.tgz)       tar xzf "$1"   ;;
        *.zip)       unzip "$1"     ;;
        *.Z)         uncompress "$1";;
        *.7z)        7z x "$1"      ;;
        *)           echo "'$1' cannot be extracted via extract()" ;;
    esac
    else
        echo "'$1' is not a valid file"
    fi
}

gdiff() {
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
}

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

# Aliases

[ "${TERM}" == "foot" ] && alias ssh="TERM=linux ssh"

# Exa
alias ls='exa'
alias ll='exa -laF'

# Grep
alias grep='grep --colour=always'
alias egrep='egrep --colour=always'
alias fgrep='fgrep --colour=always'

# Copy (confirm before overwriting)
alias cp='cp -i'

# IP (color output)
alias ip='ip -c'

# Update
alias update="sudo pacman -Syu && yay -Sua"
alias udpate="sudo pacman -Syu && yay -Sua"

# Always clears scrollback buffer
alias clear="printf '\033[2J\033[3J\033[1;1H' && afetch"
alias celar="printf '\033[2J\033[3J\033[1;1H' && afetch"
alias clearall="printf '\033[2J\033[3J\033[1;1H'"

# Cbonsai
alias cbonsai="cbonsai -li -w 1 -L 50"

# Mullvad
alias muldown="mullvad lockdown-mode set off && mullvad disconnect"
alias mulup="mullvad lockdown-mode set on && mullvad connect"
alias mulreg="mullvad tunnel wireguard key regenerate"

# Xclip
alias clip="xclip -sel c <"

# Always show progress when using dd
alias dd="sudo dd status=progress"

# Git
alias glog="git log --oneline --color=always"

afetch
