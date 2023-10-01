import os
import json
import subprocess

from setup.lib import LIB_DIR
from setup.lib.install.yay import YayInstaller

__PACMAN = "pacman"
__YAY = "yay"

__PACKAGES_FILE = f"{LIB_DIR}/../data/packages.json"


with open(__PACKAGES_FILE) as file:
    _packages_data = json.loads(file.read())


def pacman_packages():
    pacman_command = \
        ["sudo", "pacman", "-Syu"] + \
        _packages_data[__PACMAN] + \
        ["--needed"]

    subprocess.run(pacman_command)


def yay_packages():
    yayInstaller = YayInstaller()
    if not os.path.isdir(os.path.expanduser("~/yay")):
        yayInstaller.install()

    yay_command = \
        ["yay", "-Sua"] + \
        _packages_data[__YAY] + \
        ["--needed"]

    subprocess.run(yay_command)
