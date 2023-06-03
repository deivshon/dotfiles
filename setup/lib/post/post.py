from typing import Dict, List

import setup.lib.printing as printing

from setup.lib.post import USER_XINITRC, STARTUP_SCRIPT, USER_HYPRSETUP
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
    printing.colorPrint(
        "Starting post install operations...", printing.MAGENTA)

    for operation in AFTER_INSTALL_OPERATIONS:
        operation.trigger(color_style)

    printing.colorPrint("Ended post install operations...", printing.MAGENTA)


def change(colorStyle):
    printing.colorPrint("Starting post run operations...", printing.MAGENTA)

    for operation in AFTER_RUN_OPERATIONS:
        operation.trigger(colorStyle)

    printing.colorPrint("Ended post run operations...", printing.GREEN)
