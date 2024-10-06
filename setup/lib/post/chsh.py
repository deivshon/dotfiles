import subprocess

from setup.lib.post.handler import PostOperationsHandler


class ChangeShellPostOperation(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "chsh"

    @staticmethod
    def needed_in_lite() -> bool:
        return True

    @classmethod
    def _trigger_impl(cls, _):
        subprocess.run(["chsh", "--shell", "/bin/fish"])
