import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class ChangeVolPactlInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/change-vol-pactl"
    DEST_PATH = os.path.expanduser("~/.config/change-vol-pactl")

    @staticmethod
    def name() -> str:
        return "change-vol-pactl"

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
            log.error(
                f"Could not compile {cls.name()}: {e}")
            return

        log.info(f"Ended {cls.name()} compilation\n")
