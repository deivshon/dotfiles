import subprocess

from typing import List

from setup.lib import log


def __exec(command: List[str]):
    p = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)

    if p.stdout is None:
        return p

    for line in iter(p.stdout.readline, ""):
        yield line.strip()


def exec(command: List[str]):
    for line in __exec(command):
        log.subprocess_line(line)
