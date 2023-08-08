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

    def _download_impl(self, pull: bool):
        self.needsCompilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        try:
            process.exec(
                ["sudo", "make", "-C", self.DEST_PATH, "clean", "install"])
        except Exception as e:
            log.error(
                f"Could not compile {self.name()}: {e}")
            return
