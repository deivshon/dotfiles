import subprocess

from typing import List

from setup.lib import log


def __exec(command: List[str]):
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    ) as process:
        if process.stdout is None:
            return

        for line in iter(process.stdout.readline, ""):
            yield line.strip()


def exec(command: List[str]):
    for line in __exec(command):
        log.subprocess_line(line)
