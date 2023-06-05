from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class RustupPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "rustup"

    @classmethod
    def _trigger_impl(cls, _):
        process.exec(["rustup", "default", "stable"])
