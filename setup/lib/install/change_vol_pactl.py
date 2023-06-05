import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class ChangeVolPactlInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/change-vol-pactl"
    DEST_PATH = os.path.expanduser("~/.config/change-vol-pactl")

    @staticmethod
    def name() -> str:
        return "change-vol-pactl"

    @classmethod
    def _download_impl(cls):
        git_download(cls.DEST_PATH, cls.REMOTE_URL)

    @classmethod
    def _compile_impl(cls):
        try:
            process.exec(
                ["sudo", "make", "-C", cls.DEST_PATH, "clean", "install"])
        except Exception as e:
            log.error(
                f"Could not compile {cls.name()}: {e}")
            return
