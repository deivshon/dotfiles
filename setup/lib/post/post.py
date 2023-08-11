from typing import Dict, List

from setup.lib import log
from setup.lib.post.handler import PostOperationsHandler
from setup.lib.post.xinitrc import XinitrcPostOperations
from setup.lib.post.rustup import RustupPostOperations
from setup.lib.post.reflector import ReflectorPostOperations
from setup.lib.post.wallpaper import WallpaperPostOperations

AFTER_INSTALL_OPERATIONS: List[PostOperationsHandler] = [
    XinitrcPostOperations(),
    RustupPostOperations(),
    ReflectorPostOperations(),
]

AFTER_RUN_OPERATIONS: List[PostOperationsHandler] = [
    WallpaperPostOperations()
]


def install(config: Dict):
    log.info(
        f"{log.WHITE}Starting post install operations...{log.NORMAL}")

    for operation in AFTER_INSTALL_OPERATIONS:
        operation.trigger(config)

    log.info(f"{log.WHITE}Ended post install operations...")


def change(config):
    log.info(f"{log.WHITE}Starting post run operations...{log.NORMAL}")

    for operation in AFTER_RUN_OPERATIONS:
        operation.trigger(config)

    log.info(f"{log.WHITE}Ended post run operations...{log.NORMAL}")
