import os
import subprocess

from setup.lib import log
from setup.lib.install.handler import InstallHandler
from setup.lib.install.generic import git_download


class CommandCacheInstaller(InstallHandler):
    REMOTE_URL = "https://github.com/deivshon/command-cache"
    DEST_PATH = os.path.expanduser("~/.config/command-cache")

    @staticmethod
    def name() -> str:
        return "command-cache"

    @classmethod
    def _download_impl(cls):
        git_download(cls.DEST_PATH, cls.REMOTE_URL)

    @classmethod
    def _compile_impl(cls):
        try:
            subprocess.run(
                ["make", "-C", cls.DEST_PATH, "install"])
        except Exception as e:
            log.error(f"Could not compile {cls.name()}: {e}")
