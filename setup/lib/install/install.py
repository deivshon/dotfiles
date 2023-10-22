import os
import json
import subprocess

from setup.lib import LIB_DIR
from setup.lib.install.paru import ParuInstaller

__PACMAN = "pacman"
__PARU = "paru"

__PACKAGES_FILE = f"{LIB_DIR}/../data/packages.json"


with open(__PACKAGES_FILE) as file:
    _packages_data = json.loads(file.read())


def pacman_packages():
    pacman_command = \
        ["sudo", "pacman", "-Syu"] + \
        _packages_data[__PACMAN] + \
        ["--needed"]

    subprocess.run(pacman_command)


def paru_packages():
    paruInstaller = ParuInstaller()
    if not os.path.isdir(ParuInstaller.DEST_PATH):
        paruInstaller.install()

    paru_command = \
        ["paru", "-Sua"] + \
        _packages_data[__PARU] + \
        ["--needed"]

    subprocess.run(paru_command)
