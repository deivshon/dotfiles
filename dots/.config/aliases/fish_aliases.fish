#!/bin/fish

# Fish aliases

alias unset "set -e"

alias ls "exa --icons"
alias ll "exa --icons -laF"
alias grep "grep --colour=always"
alias egrep "egrep --colour=always"
alias fgrep "fgrep --colour=always"
alias cp "cp -i"
alias ip "ip -c"
alias clear "printf '\033[2J\033[3J\033[1;1H' && afetch"
alias clearall "printf '\033[2J\033[3J\033[1;1H'"
alias muldown "mullvad lockdown-mode set off && mullvad disconnect"
alias mulup "mullvad lockdown-mode set on && mullvad connect"
alias mulreg "mullvad tunnel wireguard key regenerate"
alias protup "protonvpn-cli killswitch --permanent"
alias protdown "protonvpn-cli killswitch --on"
alias clip "xclip -sel c <"
alias dd "sudo dd status=progress"
alias glog "git log --oneline --color=always"
alias sudoedit "sudo nanowrap"
