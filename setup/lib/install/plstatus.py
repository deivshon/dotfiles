import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class PlstatusInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/plstatus"
    DEST_PATH = os.path.expanduser("~/.config/plstatus")

    @staticmethod
    def name() -> str:
        return "plstatus"

    @classmethod
    def _download_impl(cls):
        git_download(cls.DEST_PATH, cls.REMOTE_URL)

    @classmethod
    def _compile_impl(cls):
        try:
            process.exec(["make", "-C", cls.DEST_PATH, "clean", "all"])
        except Exception as e:
            log.error(
                f"Could not compile {cls.name()}: {e}")
            return

        try:
            process.exec(["sudo", "make", "-C", cls.DEST_PATH, "install"])
        except Exception as e:
            log.error(
                f"Could not install {cls.name()}: {e}")
            return
