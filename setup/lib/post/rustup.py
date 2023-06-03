import subprocess

from setup.lib.post.handler import PostOperationsHandler


class RustupPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "rustup"

    @classmethod
    def _trigger_impl(cls, color_style):
        subprocess.run(["rustup", "default", "stable"])
