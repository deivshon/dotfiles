import os
import stat
import subprocess

from setup.lib import log


def get_last_node(path):
    return path[::-1][0:path[::-1].index("/")][::-1]


def get_wallpaper_path(wallpaper_name):
    return f"{os.path.expanduser('~')}/Pictures/wallpapers/{wallpaper_name}"


def sed_escape_path(str):
    # "\x5c/" = "\/", to avoid unnecessary warning
    return str.replace("/", "\x5c/")


def replace_in_file(filePath: str, regex: str, new: str) -> None:
    subprocess.run(["sed", "-iE", f"s/{regex}/{new}/g", filePath])


def make_executable(path: str, sudo: bool = False):
    if not os.path.isfile(path):
        log.error(f"Can't make {path} executable, not a file")
        return

    if sudo:
        subprocess.run(["sudo", "chmod", "+x", path])
    else:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


def makedirs(path: str):
    try:
        os.makedirs(path)
    except PermissionError:
        subprocess.run(["sudo", "mkdir", "-p", path])
