import os
import stat
import time
import shutil
import subprocess

from setup.lib import log


def get_wallpaper_path(wallpaper_name):
    return f"{os.path.expanduser('~')}/Pictures/wallpapers/{wallpaper_name}"


def replace_in_file(file_path: str, old: str, new: str) -> None:
    with open(file_path, 'r') as f:
        file_content = f.read()

    new_content = file_content.replace(old, new)

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


def write_to_file(content: str | bytes, target: str, force: bool, needs_sudo: bool) -> bool:
    write_mode = "w" if isinstance(content, str) else "wb"
    if needs_sudo:
        tmp_file = os.path.join("/tmp", str(time.time_ns()))
        with open(tmp_file, write_mode) as f:
            f.write(content)

        subprocess.run(
            ["sudo", "cp", "-f" if force else "-i", tmp_file, target])
        os.remove(tmp_file)
        return True
    else:
        if os.path.isfile(target) and not force:
            print(
                f"{target} already exists. Proceed with overwriting? [y/N]", end=" ")
            user_response = input().lower()
            if user_response != "y":
                return False

        with open(target, write_mode) as f:
            f.write(content)

        return True
