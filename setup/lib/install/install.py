import os
import json
import subprocess

from setup.lib import LIB_DIR
from setup.lib.install.yay import YayInstaller

__PACMAN = "pacman"
__YAY = "yay"

__PACKAGES_FILE = f"{LIB_DIR}/../data/packages.json"


def packages():
    with open(__PACKAGES_FILE) as f:
        packages = json.loads(f.read())

    if not os.path.isdir(os.path.expanduser("~/yay")):
        YayInstaller.install()

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
