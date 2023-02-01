# Avoid Perl locale warnings
export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

export EDITOR=nano

PATH=${PATH}:~/.local/scripts/:
PATH=${PATH}:/opt/riscv32/bin/:/opt/riscv32linux/bin/:

if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    startx 2> /dev/null
fi
