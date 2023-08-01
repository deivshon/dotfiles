import json
import os
import subprocess

from typing import List
from dataclasses import dataclass, field

from setup.lib import log
from setup.lib import LIB_DIR

__SUDO_FLAG = "sudo"


@dataclass
class Symlink():
    source: str
    target: str
    flags: List[str] = field(default_factory=list)


def __load_symlinks(path: str) -> List[Symlink]:
    with open(path, "r") as f:
        raw_symlinks = json.loads(f.read())

    symlinks: List[Symlink] = []
    for raw_symlink in raw_symlinks:
        try:
            symlink = Symlink(**raw_symlink)
        except Exception as e:
            log.failure(
                f"Could not parse symlink {json.dumps(raw_symlink, indent=4)}: {e}")
            break

        symlinks.append(symlink)

    return symlinks


__SYMLINKS_FILE = f"{LIB_DIR}/../data/symlinks.json"
__SYMLINKS = __load_symlinks(__SYMLINKS_FILE)


def apply():
    for s in __SYMLINKS:
        command = ["ln", "-s", s.source, s.target]
        if __SUDO_FLAG in s.flags:
            command = ["sudo"] + command

        if not os.path.isfile(s.source) and not os.path.isdir(s.source):
            log.warning(
                f"Can't apply symlink: source {log.YELLOW}{s.source}{log.NORMAL} does not exist")
            continue
        if os.path.isfile(s.target):
            log.warning(
                f"Can't apply symlink: target {log.YELLOW}{s.target}{log.NORMAL} already exists")
            continue
        if not os.path.isdir(os.path.dirname(s.target)):
            os.mkdir(os.path.dirname(s.target))

        p = subprocess.run(command)
        if p.returncode == 0:
            log.info(
                f"Linked {log.WHITE}{s.source}{log.NORMAL} to {log.WHITE}{s.target}")


def remove():
    for s in __SYMLINKS:
        command = ["unlink", s.target]
        if __SUDO_FLAG in s.flags:
            command = ["sudo"] + command

        if not os.path.isfile(s.target):
            continue

        p = subprocess.run(command)
        if p.returncode == 0:
            log.info(
                f"{log.WHITE}Removed {log.RED}{s.target}{log.WHITE} symlink")
