import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class StatusScriptsInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/status-scripts"
    DEST_PATH = os.path.expanduser("~/.local/repos/status-scripts")
    INSTALL_PATH = os.path.expanduser("~/.local/scripts")

    @staticmethod
    def name() -> str:
        return "status-scripts"

    def _download_impl(self, pull: bool):
        self.needs_compilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    @staticmethod
    def needed_in_lite() -> bool:
        return False

    def _compile_impl(self):
        try:
            process.exec(
                ["make", "-C", self.DEST_PATH, "install"])
        except Exception as e:
            log.error(f"Could not compile {self.name()}: {e}")
