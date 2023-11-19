import os
import json
import subprocess

from typing import Dict, Optional, List

from setup.lib import log, LIB_DIR
from setup.lib.utils import process
from setup.lib.dots.appliers.applier import Applier

__VSCODE_EXTENSIONS_FILE = os.path.join(
    LIB_DIR, "..", "data", "vscode_extensions.json")


def __get_installed_extensions() -> Optional[List[str]]:
    try:
        p = subprocess.run(["code", "--list-extensions"], capture_output=True)
    except Exception as e:
        log.error(f"Could not get current vscode extensions: {log.RED}{e}")
        return None

    return list(filter(lambda l: l != "", p.stdout.decode().splitlines()))


def __extensions_applier(_: Dict) -> None:
    if not os.path.isfile(__VSCODE_EXTENSIONS_FILE):
        log.error(
            f"Could not find VS Code extensions list file: {log.RED}{__VSCODE_EXTENSIONS_FILE}{log.NORMAL} does not exist")
        return

    with open(__VSCODE_EXTENSIONS_FILE, "r") as f:
        config_extensions: List[str] = json.loads(f.read())

    installed_extensions = __get_installed_extensions()
    if installed_extensions is None:
        return

    needing_install = list(filter(
        lambda e: e not in installed_extensions, config_extensions))

    if len(needing_install) == 0:
        log.info("All requested VS Code extensions already installed")
        return

    for extension in needing_install:
        log.info(f"Installing VS Code extension {extension}")
        try:
            process.exec(["code", "--install-extension", extension])
        except Exception as e:
            log.error(f"Could not install extension {extension}: {log.RED}{e}")


VSCODE_EXTENSIONS_APPLIER = Applier(name="vscode-extensions", required=[],
                                    apply_once=False, run=__extensions_applier)
