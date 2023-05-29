import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class YayInstaller(InstallHandler):
    REMOTE_URL = "https://aur.archlinux.org/yay.git"
    DEST_PATH = os.path.expanduser("~/yay")

    @staticmethod
    def name() -> str:
        return "yay"

    @classmethod
    def download(cls):
        log.info(f"Starting {cls.name()} download")
        git_download(cls.DEST_PATH, cls.REMOTE_URL)
        log.info(f"Ended {cls.name()} download\n")

    @classmethod
    def compile(cls):
        log.info(f"Started {cls.name()} compilation")
        if not os.path.isdir(cls.DEST_PATH):
            log.error(
                f"Could not compile {cls.name()}: {cls.DEST_PATH} does not exist")
            return

        old_cwd = os.getcwd()
        os.chdir(cls.DEST_PATH)
        try:
            subprocess.run(["makepkg", "-si"], check=True)
        except subprocess.CalledProcessError as e:
            log.error(f"An error occurred in makepkg while building yay: {e}")
        except Exception as e:
            log.error(f"An unknown error occurred while building yay: {e}")
        finally:
            os.chdir(old_cwd)

        log.info(f"Ended {cls.name()} compilation\n")
