import sys
import subprocess
import os
import json
from time import time as currentTimestamp

__PACMAN = "pacman"
__YAY = "yay"
__acceptedInstallPrograms = [
    "yay",
    "dwm",
    "plstatus",
    "change_vol_pactl",
    "st",
    "status_scripts",
    "command_cache"
]

__PACKAGES_FILE = "./setup/data/packages.json"
__INSTALLS_SCRIPT = "./setup/installs.sh"


def __script(program, action):
    if program not in __acceptedInstallPrograms:
        sys.exit(f"Program {program} can't be installed")

    subprocess.run([__INSTALLS_SCRIPT, program, action])


def install(program):
    __script(program, "i")


def download(program):
    __script(program, "d")


def compile(program):
    __script(program, "c")


def packages():
    with open(__PACKAGES_FILE) as f:
        packages = json.loads(f.read())

    if not os.path.isdir(os.path.expanduser("~/yay")):
        install("yay")

    pacmanCommand = \
        ["sudo", "pacman", "-Syu"] + \
        packages[__PACMAN] + \
        ["--needed"]

    yayCommand = \
        ["yay", "-Sua"] + \
        packages[__YAY] + \
        ["--needed"]

    subprocess.run(pacmanCommand)
    subprocess.run(yayCommand)


def status_scripts():
    install("status_scripts")

    # Needed to allow correct plstatus compilation
    os.environ["PATH"] += ":" + os.path.expanduser("~/.local/scripts")
