import os
import subprocess

from setup.lib import log
from setup.lib.utils import process


def git_download(path: str, link: str):
    if not os.path.isdir(path):
        try:
            process.exec(["git", "clone", link, path])
        except Exception as e:
            log.warning(
                f"An error occurred while trying to clone repository at {link}: {e}")
    else:
        if os.path.isdir(f"{path}/.git"):
            log.info(f"{path} already exists, pulling")
            try:
                process.exec(["git", "-C", path, "pull"])
            except Exception as e:
                log.warning(
                    f"An error occurred while trying to pull repository at {link}: {e}")
        else:
            log.warning(
                f"{path} already exists and does not seem to be a git repository, aborting download")
