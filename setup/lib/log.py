import sys
import subprocess
from typing import NoReturn


__tput_warning = False
try:
    RED = subprocess.run(["tput", "setaf", "1", "bold"],
                         capture_output=True).stdout.decode()
    GREEN = subprocess.run(["tput", "setaf", "2", "bold"],
                           capture_output=True).stdout.decode()
    YELLOW = subprocess.run(["tput", "setaf", "3", "bold"],
                            capture_output=True).stdout.decode()
    BLUE = subprocess.run(["tput", "setaf", "4", "bold"],
                          capture_output=True).stdout.decode()
    MAGENTA = subprocess.run(
        ["tput", "setaf", "5", "bold"], capture_output=True).stdout.decode()
    CYAN = subprocess.run(["tput", "setaf", "6", "bold"],
                          capture_output=True).stdout.decode()
    WHITE = subprocess.run(["tput", "setaf", "7", "bold"],
                           capture_output=True).stdout.decode()
    NORMAL = subprocess.run(
        ["tput", "sgr0"], capture_output=True).stdout.decode()
except Exception as e:
    RED = "\033[1m\033[31m"
    GREEN = "\033[1m\033[32m"
    YELLOW = "\033[1m\033[33m"
    BLUE = "\033[1m\033[34m"
    MAGENTA = "\033[1m\033[35m"
    CYAN = "\033[1m\033[36m"
    WHITE = "\033[1m\033[37m"
    NORMAL = "\033[0m"
    __tput_warning = True


def warning(msg: str):
    print(f"{WHITE}[{YELLOW}!{WHITE}]{NORMAL} {msg}{NORMAL}")


def info(msg: str):
    print(f"{WHITE}[{BLUE}>{WHITE}]{NORMAL} {msg}{NORMAL}")


def error(msg: str):
    print(f"{WHITE}[{RED}!{WHITE}]{NORMAL} {msg}{NORMAL}")


def failure(msg: str) -> NoReturn:
    error(f"{RED}FATAL ERROR OCCURRED{NORMAL}")
    error(msg)
    sys.exit(1)


def subprocess_line(line: str, is_stderr: bool):
    if is_stderr:
        print(f" {RED}-->{NORMAL} {line}")
    else:
        print(f" {BLUE}-->{NORMAL} {line}")


if __tput_warning:
    warning("Could not use tput to generate color codes")

del __tput_warning
