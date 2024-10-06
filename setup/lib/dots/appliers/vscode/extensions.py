import os
import json
import subprocess

from dataclasses import dataclass
from typing import Dict, Optional, List

from setup.lib import utils
from setup.lib import log, LIB_DIR
from setup.lib.utils import process
from setup.lib.dots.appliers.applier import Applier

__VSCODE_EXTENSIONS_FILE = os.path.join(
    LIB_DIR, "..", "data", "vscode_extensions.json")
__VSCODE_INSTALLED_EXTENSIONS_FILE = os.path.join(
    utils.HOME_DIR, ".vscode", "extensions", "extensions.json")
__VSCODE_EXTENSION_IDENTIFIER_LABEL = "identifier"


@dataclass
class _ExtensionIdentificationData():
    id: str
    uuid: str


def __get_installed_extensions() -> Optional[List[str]]:
    try:
        installed_extensions: List[str] = []
        if os.path.isfile(__VSCODE_INSTALLED_EXTENSIONS_FILE):
            with open(__VSCODE_INSTALLED_EXTENSIONS_FILE) as f:
                installed_extensions_data = json.loads(f.read())

            for raw_extension_data in installed_extensions_data:
                if __VSCODE_EXTENSION_IDENTIFIER_LABEL not in raw_extension_data:
                    continue

                extension_identifier = raw_extension_data[__VSCODE_EXTENSION_IDENTIFIER_LABEL]
                extension_data = _ExtensionIdentificationData(
                    **extension_identifier)
                installed_extensions.append(extension_data.id)

            return installed_extensions
        else:
            log.warning(
                f"Could not get current vscode extensions from file: {log.RED}{__VSCODE_INSTALLED_EXTENSIONS_FILE} does not exist")
    except Exception as e:
        log.error(
            f"Could not get current vscode extensions from file: {log.RED}{e}")
        log.error(f"Falling back `code --list-extensions` command")

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
    config_extensions = list(map(lambda e: e.lower(), config_extensions))

    installed_extensions = __get_installed_extensions()
    if installed_extensions is None:
        return

    installed_extensions = list(map(lambda e: e.lower(), installed_extensions))

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
                                    apply_once=False, run=__extensions_applier, needed_in_lite=True)
