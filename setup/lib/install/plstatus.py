import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class PlstatusInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/plstatus"
    DEST_PATH = os.path.expanduser("~/.config/plstatus")

    @staticmethod
    def name() -> str:
        return "plstatus"

    @classmethod
    def download(cls):
        log.info(f"Starting {cls.name()} download")
        git_download(cls.DEST_PATH, cls.REMOTE_URL)
        log.info(f"Ended {cls.name()} download\n")

    @classmethod
    def compile(cls):
        log.info(f"Starting {cls.name()} compilation")
        try:
            subprocess.run(["make", "-C", cls.DEST_PATH, "clean", "all"])
        except Exception as e:
            log.error(
                f"Could not compile {cls.name()}: {e}")
            return

        try:
            subprocess.run(["sudo", "make", "-C", cls.DEST_PATH, "install"])
        except Exception as e:
            log.error(
                f"Could not install {cls.name()}: {e}")
            return

        log.info(f"Ended {cls.name()} compilation\n")
