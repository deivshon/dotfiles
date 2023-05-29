import os
import subprocess

from setup.lib import log


def git_download(path: str, link: str):
    if not os.path.isdir(path):
        try:
            subprocess.run(["git", "clone", link, path], check=True)
        except subprocess.CalledProcessError as e:
            log.warning(
                f"A git error occurred trying to clone repository at {link}: {e}")
        except Exception as e:
            log.warning(
                f"An unknown error occurred trying to clone repository at {link}: {e}")
    else:
        if os.path.isdir(f"{path}/.git"):
            log.info(f"{path} already exists, pulling")
            try:
                subprocess.run(["git", "-C", path, "pull"])
            except subprocess.CalledProcessError as e:
                log.warning(
                    f"A git error occurred trying to pull repository at {link}: {e}")
            except Exception as e:
                log.warning(
                    f"An unknown error occurred trying to pull repository at {link}: {e}")
        else:
            log.warning(
                f"{path} already exists and does not seem to be a git repository, aborting download")
