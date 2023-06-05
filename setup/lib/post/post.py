from typing import Dict, List

from setup.lib import log
from setup.lib.post.handler import PostOperationsHandler
from setup.lib.post.xinitrc import XinitrcPostOperations
from setup.lib.post.startup_script import StatusScriptsPostOperations
from setup.lib.post.rustup import RustupPostOperations
from setup.lib.post.reflector import ReflectorPostOperations
from setup.lib.post.hyprland import HyprlandPostOperations
from setup.lib.post.bash import BashPostOperations
from setup.lib.post.wallpaper import WallpaperPostOperations

AFTER_INSTALL_OPERATIONS: List[PostOperationsHandler] = [
    XinitrcPostOperations(),
    StatusScriptsPostOperations(),
    RustupPostOperations(),
    ReflectorPostOperations(),
    BashPostOperations(),
    HyprlandPostOperations()
]

AFTER_RUN_OPERATIONS: List[PostOperationsHandler] = [
    WallpaperPostOperations()
]


def install(color_style: Dict):
    log.info(
        f"{log.MAGENTA}Starting post install operations...{log.NORMAL}")

    for operation in AFTER_INSTALL_OPERATIONS:
        operation.trigger(color_style)

    log.info(f"{log.MAGENTA}Ended post install operations...")


def change(color_style):
    log.info(f"{log.MAGENTA}Starting post run operations...{log.NORMAL}")

    for operation in AFTER_RUN_OPERATIONS:
        operation.trigger(color_style)

    log.info(f"{log.GREEN}Ended post run operations...{log.NORMAL}")
