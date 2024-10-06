import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class CommandCacheInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/command-cache"
    DEST_PATH = os.path.expanduser("~/.local/repos/command-cache")

    @staticmethod
    def name() -> str:
        return "command-cache"

    @staticmethod
    def needed_in_lite() -> bool:
        return False

    def _download_impl(self, pull: bool):
        self.needs_compilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        try:
            process.exec(
                ["make", "-C", self.DEST_PATH, "install"])
        except Exception as e:
            log.error(f"Could not compile {self.name()}: {e}")
