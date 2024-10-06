import os

from setup.lib import log
from setup.lib.utils import process
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class AliasRsInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/alias-rs"
    DEST_PATH = os.path.expanduser("~/.local/repos/alias-rs")

    @staticmethod
    def name() -> str:
        return "alias-rs"

    @staticmethod
    def needed_in_lite() -> bool:
        return True

    def _download_impl(self, pull: bool):
        self.needs_compilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        try:
            process.exec(["make", "-C", self.DEST_PATH, "clean", "all"])
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
