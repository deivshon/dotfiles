import os
import json
import subprocess

from setup.lib import LIB_DIR
from setup.lib.install.yay import YayInstaller

__PACMAN = "pacman"
__YAY = "yay"

__PACKAGES_FILE = f"{LIB_DIR}/../data/packages.json"


def packages():
    with open(__PACKAGES_FILE) as file:
        packages_data = json.loads(file.read())

    if not os.path.isdir(os.path.expanduser("~/yay")):
        YayInstaller.install()

    pacman_command = \
        ["sudo", "pacman", "-Syu"] + \
        packages_data[__PACMAN] + \
        ["--needed"]

    yay_command = \
        ["yay", "-Sua"] + \
        packages_data[__YAY] + \
        ["--needed"]

    subprocess.run(pacman_command)
    subprocess.run(yay_command)
