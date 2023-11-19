import os

from setup.lib import log
from setup.lib.utils import process

__PULL_NO_CHANGES = "Already up to date."


def git_download(path: str, link: str, pull: bool) -> bool:
    if not os.path.isdir(path):
        try:
            process.exec(["git", "clone", link, path])
            return True
        except Exception as e:
            log.warning(
                f"An error occurred while trying to clone repository at {link}: {e}")
    else:
        if os.path.isdir(f"{path}/.git"):
            if pull:
                log.info(f"{path} already exists, pulling")
                try:
                    output = process.exec(["git", "-C", path, "pull"])
                    return output[process.EXEC_STDOUT] != __PULL_NO_CHANGES
                except Exception as e:
                    log.warning(
                        f"An error occurred while trying to pull repository at {link}: {e}")
            else:
                log.info(f"{path} already exists, not pulling")
        else:
            log.warning(
                f"{path} already exists and does not seem to be a git repository, aborting download")

    return False
