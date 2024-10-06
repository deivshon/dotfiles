from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class RustupPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "rustup"

    @staticmethod
    def needed_in_lite() -> bool:
        return True

    @classmethod
    def _trigger_impl(cls, _):
        process.exec(["rustup", "default", "stable"])
