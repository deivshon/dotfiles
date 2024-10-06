from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class ReflectorPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "reflector"

    @staticmethod
    def needed_in_lite() -> bool:
        return True

    @classmethod
    def _trigger_impl(cls, _):
        process.exec(["sudo", "systemctl", "enable", "reflector.service"])
