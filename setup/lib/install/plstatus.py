import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class PlstatusInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/plstatus"
    DEST_PATH = os.path.expanduser("~/.local/repos/plstatus")

    @staticmethod
    def name() -> str:
        return "plstatus"

    def _download_impl(self, pull: bool):
        self.needsCompilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        try:
            process.exec(["make", "-C", self.DEST_PATH, "clean", "release"])
        except Exception as e:
            log.error(
                f"Could not compile {self.name()}: {e}")
            return

        try:
            process.exec(["sudo", "make", "-C", self.DEST_PATH, "install"])
        except Exception as e:
            log.error(
                f"Could not install {self.name()}: {e}")
            return
