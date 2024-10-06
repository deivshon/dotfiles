import json
import os
import subprocess

from typing import List
from dataclasses import dataclass, field

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.symlinks.flags import SUDO_FLAG, FORCE_FLAG


@dataclass
class Symlink():
    source: str
    target: str
    needed_in_lite: bool
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


def apply(lite_mode: bool):
    for s in __SYMLINKS:
        if lite_mode and not s.needed_in_lite:
            continue

        ln_flags = "-s"
        if FORCE_FLAG in s.flags:
            ln_flags += "f"

        link = ["ln", ln_flags, s.source, s.target]

        if SUDO_FLAG in s.flags:
            link.insert(0, "sudo")

        if not os.path.isfile(s.source) and not os.path.isdir(s.source):
            log.warning(
                f"Can't apply symlink: source {log.YELLOW}{s.source}{log.NORMAL} does not exist")
            continue
        if os.path.isfile(s.target):
            if os.path.islink(s.target) and os.readlink(s.target) == s.source:
                log.info(
                    f"Link {log.WHITE}{s.source}{log.NORMAL} to {log.WHITE}{s.target}{log.NORMAL} already exists")
                continue

            if FORCE_FLAG not in s.flags:
                log.warning(
                    f"Can't link {log.WHITE}{s.source}{log.NORMAL} to {log.YELLOW}{s.target}{log.NORMAL}: target exists")
                continue

        if not os.path.isdir(os.path.dirname(s.target)):
            utils.path.makedirs(os.path.dirname(s.target))

        p = subprocess.run(link, capture_output=True)
        if p.returncode != 0:
            log.error(
                f"Could not link {log.WHITE}{s.source}{log.NORMAL} to {log.WHITE}{s.target}")
        else:
            log.info(
                f"Linked {log.WHITE}{s.source}{log.NORMAL} to {log.WHITE}{s.target}")


def remove():
    for s in __SYMLINKS:
        command = ["unlink", s.target]
        if SUDO_FLAG in s.flags:
            command.insert(0, "sudo")

        if not os.path.islink(s.target):
            continue
        if os.readlink(s.target) == s.target:
            continue

        p = subprocess.run(command)
        if p.returncode == 0:
            log.info(
                f"{log.WHITE}Removed {log.RED}{s.target}{log.WHITE} symlink")
