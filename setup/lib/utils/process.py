import select
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

        read_streams = [process.stdout, process.stderr]

        while read_streams:
            readable, _, _ = select.select(read_streams, [], [])
            for stream in readable:
                line = stream.readline().rstrip()
                if not line:
                    read_streams.remove(stream)
                else:
                    yield line, stream == process.stderr


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
