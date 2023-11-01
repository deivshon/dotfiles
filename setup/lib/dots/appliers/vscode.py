import json
import os

from typing import Dict, List

from setup.lib import log
from setup.lib.utils import HOME_DIR
from setup.lib.dots.appliers.applier import Applier

__VSCODE_THEME = "vscode-theme"
__VSCODE_REQUIRED: List[str] = [
    __VSCODE_THEME
]

__VSCODE_SETTINGS_FILE = os.path.join(
    HOME_DIR, ".config", "Code", "User", "settings.json")
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


VSCODE_APPLIER = Applier(name="vscode", required=__VSCODE_REQUIRED,
                         apply_once=False, run=__theme_applier)
