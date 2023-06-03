import subprocess

from setup.lib.post.handler import PostOperationsHandler


class ReflectorPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "reflector"

    @classmethod
    def _trigger_impl(cls, color_style):
        subprocess.run(["sudo", "systemctl", "enable", "reflector.service"])
