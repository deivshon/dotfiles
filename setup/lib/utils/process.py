import subprocess

from typing import List, Tuple

from setup.lib import log

EXEC_STDOUT = 0
EXEC_STDERR = 1


def __exec(command: List[str]):
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    ) as process:
        if process.stdout is None or process.stderr is None:
            return

        for line in iter(process.stdout.readline, ""):
            yield line.rstrip(), False

        for line in iter(process.stderr.readline, ""):
            yield line.rstrip(), True


def exec(command: List[str]) -> Tuple[str, str]:
    stdout = ""
    stderr = ""
    for line, is_stderr in __exec(command):
        log.subprocess_line(line, is_stderr)
        if is_stderr:
            stderr += line
        else:
            stdout += line

    return stdout, stderr
