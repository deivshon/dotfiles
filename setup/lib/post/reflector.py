from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class ReflectorPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "reflector"

    @classmethod
    def _trigger_impl(cls, _):
        process.exec(["sudo", "systemctl", "enable", "reflector.service"])
