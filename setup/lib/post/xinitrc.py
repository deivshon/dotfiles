import os

from setup.lib import log
from setup.lib.post import USER_XINITRC, DEFAULT_XINITRC, XINITRC_APPEND
from setup.lib.post.handler import PostOperationsHandler


class XinitrcPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "xinitrc"

    @classmethod
    def _trigger_impl(cls, _):
        if os.path.isfile(USER_XINITRC):
            log.warning(
                f"{log.RED}{USER_XINITRC} already exists{log.NORMAL}")
            return

        if not os.path.isfile(DEFAULT_XINITRC):
            log.error(
                f"{log.RED}Couldn't handle xinitrc: default xinitrc not found{log.NORMAL}")
            return

        with open(DEFAULT_XINITRC) as file:
            xinitrc = file.read().splitlines()

        if "twm &" not in xinitrc:
            log.error(
                f"{log.RED}Couldn't handle xinitrc: malformed default xinitrc{log.NORMAL}")
            return

        xinitrc = xinitrc[0:xinitrc.index("twm &")]

        with open(XINITRC_APPEND, "r") as file:
            xinitrc_append = file.read()

        with open(USER_XINITRC, "w") as file:
            file.write("\n".join(xinitrc) + "\n" + xinitrc_append)
