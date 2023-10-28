import os
import json

from typing import List
from typing import Dict

from setup.lib import log
from setup.lib import LIB_DIR
from setup.lib.config.expansion import EXPANSION_DATA
from setup.lib.config import SUBSTITUTIONS, EXPECTED_SUBSTITUTIONS
from setup.lib.config.expansion.efy import EfyColors
from setup.lib.config.expansion.user import SetupUser
from setup.lib.config.expansion.wallpaper import WallpaperPath
from setup.lib.config.expansion.firefox import FirefoxColors
from setup.lib.config.expansion.swaylock import SwayLockColors
from setup.lib.config.expansion.handler import ExpansionHandler
from setup.lib.config.expansion.colors_no_hash import ColorsNoHash

__CONFIG_FILE = f"{LIB_DIR}/../data/configFields.json"
__EXPANSIONS: List[ExpansionHandler] = [
    EfyColors(),
    WallpaperPath(),
    ColorsNoHash(),
    FirefoxColors(),
    SwayLockColors(),
    SetupUser(),
]
__DEFAULTS_PATHS: List[str] = [
    "terminal_colors.json",
    "btop.json",
    "dwm.json",
    "firefox.json",
    "rofi.json"
]


def check(config):
    with open(__CONFIG_FILE, "r") as file:
        expected_data = json.loads(file.read())

    for field in expected_data:
        if field not in config.keys():
            log.failure("Field missing in config: " + field)

    for field in EXPECTED_SUBSTITUTIONS:
        if field not in config[SUBSTITUTIONS].keys():
            log.failure("Sub-field missing in substitutions field: " + field)


def expand(config):
    for expansion in __EXPANSIONS:
        expansion.expand(config, EXPANSION_DATA)


def apply_defaults(config: Dict) -> None:
    path_prefix = "./data/defaults"
    for path in __DEFAULTS_PATHS:
        with open(f"{path_prefix}/{path}") as f:
            current_fields = json.loads(f.read())

        for key, value in current_fields.items():
            if key not in config[SUBSTITUTIONS]:
                config[SUBSTITUTIONS][key] = value


def apply_preset(config: Dict, preset_name: str) -> None:
    preset_path = f"./data/presets/{preset_name}.json"
    if not os.path.isfile(preset_path):
        log.failure(f"Preset {preset_name} does not exist")

    log.info(f"Applying preset {log.GREEN}{preset_name}")
    with open(preset_path) as f:
        preset = json.loads(f.read())

    for key, value in preset.items():
        if key not in config[SUBSTITUTIONS]:
            config[SUBSTITUTIONS][key] = value


def initialize(config: Dict):
    if SUBSTITUTIONS not in config:
        config[SUBSTITUTIONS] = {}
