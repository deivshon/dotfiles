from typing import Dict, List

from setup.lib import log
from setup.lib.post.chsh import ChangeShellPostOperation
from setup.lib.post.handler import PostOperationsHandler
from setup.lib.post.xinitrc import XinitrcPostOperations
from setup.lib.post.rustup import RustupPostOperations
from setup.lib.post.reflector import ReflectorPostOperations
from setup.lib.post.wallpaper import WallpaperPostOperations

AFTER_INSTALL_OPERATIONS: List[PostOperationsHandler] = [
    XinitrcPostOperations(),
    ReflectorPostOperations(),
    ChangeShellPostOperation(),
]

AFTER_PACKAGES_OPERATIONS: List[PostOperationsHandler] = [
    RustupPostOperations(),
]

AFTER_RUN_OPERATIONS: List[PostOperationsHandler] = [
    WallpaperPostOperations()
]


def _generic_install(config: Dict, operations_label: str, operations_list: List[PostOperationsHandler]):
    log.info(
        f"{log.WHITE}Starting {operations_label} operations...{log.NORMAL}")

    for operation in operations_list:
        operation.trigger(config)

    log.info(f"{log.WHITE}Ended {operations_label} operations...")


def after_packages_install(config: Dict):
    _generic_install(config, "post packages install",
                     AFTER_PACKAGES_OPERATIONS)


def install(config: Dict):
    _generic_install(config, "post install", AFTER_INSTALL_OPERATIONS)


def change(config):
    _generic_install(config, "post run", AFTER_RUN_OPERATIONS)
