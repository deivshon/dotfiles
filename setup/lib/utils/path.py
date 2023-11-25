import os
import re
import stat
import mmap
import shutil
import subprocess

from setup.lib import log


def get_wallpaper_path(wallpaper_name):
    return f"{os.path.expanduser('~')}/Pictures/wallpapers/{wallpaper_name}"


def replace_in_file(file_path: str, regex: str, new: str) -> None:
    with open(file_path, 'r') as f:
        file_content = f.read()

    new_content = re.sub(regex, new, file_content)

    with open(file_path, "w") as f:
        f.write(new_content)


def make_executable(path: str, sudo: bool = False):
    if not os.path.isfile(path):
        log.error(f"Can't make {path} executable, not a file")
        return

    if sudo:
        subprocess.run(["sudo", "chmod", "+x", path])
    else:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


def make_non_executable(path: str, sudo: bool = False):
    if not os.path.isfile(path):
        log.error(f"Can't make {path} non executable, not a file")
        return

    if sudo:
        subprocess.run(["sudo", "chmod", "-x", path])
    else:
        os.chmod(path, os.stat(path).st_mode & ~stat.S_IEXEC)


def makedirs(path: str):
    try:
        os.makedirs(path)
    except PermissionError:
        subprocess.run(["sudo", "mkdir", "-p", path])


def copy(source: str, target: str, force: bool, needs_sudo: bool) -> bool:
    if needs_sudo:
        subprocess.run(["sudo", "cp", "-f" if force else "-i", source, target])
        return True
    else:
        if os.path.isfile(target) and not force:
            print(
                f"{target} already exists. Proceed with copy? [y/N]", end=" ")
            user_response = input().lower()
            if user_response != "y":
                return False

        shutil.copy(source, target)
        return True
