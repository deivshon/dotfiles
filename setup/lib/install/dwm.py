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

    @classmethod
    @abstractmethod
    def _download_impl(cls):
        git_download(cls.DEST_PATH, cls.REMOTE_URL)

    @classmethod
    @abstractmethod
    def _compile_impl(cls):
        try:
            process.exec(
                ["sudo", "make", "-C", cls.DEST_PATH, "clean", "install"])
        except Exception as e:
            log.error(f"Could not compile {cls.name()}: {e}")
