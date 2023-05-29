import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class StInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/st"
    DEST_PATH = os.path.expanduser("~/.config/st")

    @staticmethod
    def name() -> str:
        return "st"

    @classmethod
    def download(cls):
        log.info(f"Starting {cls.name()} download")
        git_download(cls.DEST_PATH, cls.REMOTE_URL)
        log.info(f"Ended {cls.name()} download\n")

    @classmethod
    def compile(cls):
        log.info(f"Starting {cls.name()} compilation")
        try:
            subprocess.run(
                ["sudo", "make", "-C", cls.DEST_PATH, "clean", "install"])
        except Exception as e:
            log.error(f"Could not compile {cls.name()}: {e}")

        log.info(f"Ended {cls.name()} compilation\n")
