import json
import os
from typing import Dict, List

from setup.lib import log
from setup.lib.dots.appliers.applier import Applier

__VSCODE_THEME = "vscode-theme"

__VSCODE_NAME = "vscode"
__VSCODE_REQUIRED: List[str] = [
    __VSCODE_THEME
]

__SETTINGS_FILE = "settings.json"
__VSCODE_CONFIG_DIR = [".config", "Code", "User"]
__SETTINGS_THEME = "workbench.colorTheme"


def __theme_applier(config_substitutions: Dict) -> None:
    code_dir = os.path.join(os.path.expanduser(
        "~"), *__VSCODE_CONFIG_DIR)

    if not os.path.isdir(code_dir):
        log.error(
            f"Could not find VS Code directory: {log.RED}{code_dir}{log.NORMAL} does not exist")
        return

    settings_file = os.path.join(code_dir, __SETTINGS_FILE)
    if not os.path.isfile(settings_file):
        log.error(
            f"Could not find VS Code settings file: {log.RED}{settings_file}{log.NORMAL} does not exist")
        return

    with open(settings_file) as f:
        vscode_settings = json.loads(f.read())

    vscode_settings[__SETTINGS_THEME] = config_substitutions[__VSCODE_THEME]

    with open(settings_file, "w") as f:
        f.write(json.dumps(vscode_settings, indent=4))


VSCODE_APPLIER = Applier(name=__VSCODE_NAME, required=__VSCODE_REQUIRED,
                         apply_once=False, run=__theme_applier)
