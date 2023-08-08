import os

from abc import abstractmethod

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class DwmInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/dwm-flexipatch"
    DEST_PATH = os.path.expanduser("~/.config/dwm")

    @staticmethod
    def name() -> str:
        return "dwm"

    def _download_impl(self, pull: bool):
        self.needsCompilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        try:
            process.exec(
                ["sudo", "make", "-C", self.DEST_PATH, "clean", "install"])
        except Exception as e:
            log.error(f"Could not compile {self.name()}: {e}")
