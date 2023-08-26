import subprocess

from setup.lib.post.handler import PostOperationsHandler


class ChangeShellPostOperation(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "chsh"

    @classmethod
    def _trigger_impl(cls, _):
        subprocess.run(["chsh", "--shell", "/bin/fish"])
