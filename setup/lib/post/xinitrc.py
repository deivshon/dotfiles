import os

from setup.lib import log
from setup.lib.post import USER_XINITRC, DEFAULT_XINITRC, XINITRC_APPEND
from setup.lib.post.handler import PostOperationsHandler


class XinitrcPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "xinitrc"

    @classmethod
    def _trigger_impl(cls, color_style):
        if os.path.isfile(USER_XINITRC):
            log.warning(
                f"{log.RED}{USER_XINITRC} already exists{log.NORMAL}")
            return

        if not os.path.isfile(DEFAULT_XINITRC):
            log.error(
                f"{log.RED}Couldn't handle xinitrc: default xinitrc not found{log.NORMAL}")
            return

        with open(DEFAULT_XINITRC) as f:
            xinitrc = f.read().splitlines()

        if "twm &" not in xinitrc:
            log.error(
                f"{log.RED}Couldn't handle xinitrc: malformed default xinitrc{log.NORMAL}")
            return

        xinitrc = xinitrc[0:xinitrc.index("twm &")]

        with open(XINITRC_APPEND, "r") as f:
            xinitrc_append = f.read()

        with open(USER_XINITRC, "w") as f:
            f.write("\n".join(xinitrc) + "\n" + xinitrc_append)
