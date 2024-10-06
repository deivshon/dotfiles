import json
import os

from typing import Dict, List

from setup.lib import log
from setup.lib.utils import HOME_DIR
from setup.lib.dots.appliers.applier import Applier
from setup.lib.const.setup_data import SHARED_DATA_DIR

__VSCODE_THEME = "vscode-theme"
__VSCODE_REQUIRED: List[str] = [
    __VSCODE_THEME
]

__VSCODE_SETTINGS_FILE = os.path.join(
    HOME_DIR, ".config", "Code", "User", "settings.json")
__VSCODE_CONFIG_SETTINGS_FILE = os.path.join(
    SHARED_DATA_DIR, "vscode-settings.json"
)
__SETTINGS_THEME = "workbench.colorTheme"


def __theme_applier(config_substitutions: Dict) -> None:
    if not os.path.isfile(__VSCODE_SETTINGS_FILE):
        log.error(
            f"Could not find VS Code settings file: {log.RED}{__VSCODE_SETTINGS_FILE}{log.NORMAL} does not exist")
        return

    with open(__VSCODE_SETTINGS_FILE) as f:
        vscode_settings = json.loads(f.read())

    vscode_settings[__SETTINGS_THEME] = config_substitutions[__VSCODE_THEME]

    log.info(
        f"Applying VS Code theme {log.YELLOW}{config_substitutions[__VSCODE_THEME]}{log.NORMAL} ({__VSCODE_SETTINGS_FILE})")
    with open(__VSCODE_SETTINGS_FILE, "w") as f:
        f.write(json.dumps(vscode_settings, indent=4))


def __settings_applier(_) -> None:
    if not os.path.isfile(__VSCODE_SETTINGS_FILE):
        log.error(
            f"Could not find VS Code settings file: {log.RED}{__VSCODE_SETTINGS_FILE}{log.NORMAL} does not exist")
        return
    if not os.path.isfile(__VSCODE_CONFIG_SETTINGS_FILE):
        log.error(
            f"Could not find VS Code config settings file: {log.RED}{__VSCODE_CONFIG_SETTINGS_FILE}{log.NORMAL} does not exist")
        return

    with open(__VSCODE_SETTINGS_FILE) as f:
        vscode_settings = json.loads(f.read())
    with open(__VSCODE_CONFIG_SETTINGS_FILE) as f:
        vscode_config_settings: Dict = json.loads(f.read())

    for key, value in vscode_config_settings.items():
        vscode_settings[key] = value

    log.info(
        f"Applying VS Code settings ({__VSCODE_SETTINGS_FILE})")
    with open(__VSCODE_SETTINGS_FILE, "w") as f:
        f.write(json.dumps(vscode_settings, indent=4))


VSCODE_THEME_APPLIER = Applier(name="vscode-theme", required=__VSCODE_REQUIRED,
                               apply_once=False, run=__theme_applier)
VSCODE_SETTINGS_APPLIER = Applier(name="vscode-settings", required=[],
                                  apply_once=False, run=__settings_applier)
