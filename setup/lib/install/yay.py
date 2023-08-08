import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class YayInstaller(InstallHandler):
    REMOTE_URL = "https://aur.archlinux.org/yay.git"
    DEST_PATH = os.path.expanduser("~/yay")

    @staticmethod
    def name() -> str:
        return "yay"

    def _download_impl(self, pull: bool):
        self.needsCompilation = git_download(
            self.DEST_PATH, self.REMOTE_URL, pull)

    def _compile_impl(self):
        if not os.path.isdir(self.DEST_PATH):
            log.error(
                f"Could not compile {self.name()}: {self.DEST_PATH} does not exist")
            return

        old_cwd = os.getcwd()
        os.chdir(self.DEST_PATH)
        try:
            subprocess.run(["makepkg", "-si"], check=True)
        except subprocess.CalledProcessError as e:
            log.error(f"An error occurred in makepkg while building yay: {e}")
        except Exception as e:
            log.error(f"An unknown error occurred while building yay: {e}")
        finally:
            os.chdir(old_cwd)
