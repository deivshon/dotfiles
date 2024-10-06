import os
import json

from typing import List
from typing import Dict
from pathlib import Path

from setup.lib import log
from setup.lib import LIB_DIR
from setup.lib.dots.appliers import APPLIERS
from setup.lib.config.expansion.efy import EfyColors
from setup.lib.config.expansion.user import SetupUser
from setup.lib.config.expansion import EXPANSION_DATA
from setup.lib.const.config import CONFIG_SUBSTITUTIONS, DOTFILES_LITE_MODE_KEY
from setup.lib.const.dots import DOT_LINKS_FILE, LINK_SUBS
from setup.lib.config.expansion.wallpaper import WallpaperPath
from setup.lib.config.expansion.firefox import FirefoxColors
from setup.lib.config.expansion.swaylock import SwayLockColors
from setup.lib.config.expansion.handler import ExpansionHandler
from setup.lib.config.expansion.colors_no_hash import ColorsNoHash

__CONFIG_FILE = f"{LIB_DIR}/../data/configFields.json"
__PRESETS_DIRECTORY = f"./data/presets"
__DEFAULTS_DIRECTORY = "./data/defaults"
__EXPANSIONS: List[ExpansionHandler] = [
    EfyColors(),
    WallpaperPath(),
    ColorsNoHash(),
    FirefoxColors(),
    SwayLockColors(),
    SetupUser(),
]

with open(DOT_LINKS_FILE, "r") as file:
    links_list = json.loads(file.read())

__EXPECTED_SUBSTITUTIONS = []
for link in links_list:
    if LINK_SUBS not in links_list[link]:
        continue

    for sub in links_list[link][LINK_SUBS]:
        if sub in __EXPECTED_SUBSTITUTIONS:
            continue

        __EXPECTED_SUBSTITUTIONS += [sub]

__DEFAULT_FIELDS: Dict[str, str] = {}
for defaults_filename in os.listdir(__DEFAULTS_DIRECTORY):
    defaults_path = f"{__DEFAULTS_DIRECTORY}/{defaults_filename}"
    if not os.path.isfile(defaults_path) or not defaults_path.endswith(".json"):
        continue

    with open(defaults_path) as f:
        current_default = json.loads(f.read())
    __DEFAULT_FIELDS.update(current_default)

__PRESETS: Dict[str, Dict[str, str]] = {}
for preset_filename in os.listdir(__PRESETS_DIRECTORY):
    preset_name = Path(preset_filename).stem
    preset_path = f"{__PRESETS_DIRECTORY}/{preset_filename}"
    if not os.path.isfile(preset_path) or not preset_path.endswith(".json"):
        continue

    with open(preset_path) as f:
        current_preset = json.loads(f.read())
    __PRESETS[preset_name] = current_preset


def check(config):
    with open(__CONFIG_FILE, "r") as file:
        expected_data = json.loads(file.read())

    for field in expected_data:
        if field not in config.keys():
            log.failure("Field missing in config: " + field)

    for field in __EXPECTED_SUBSTITUTIONS:
        if field not in config[CONFIG_SUBSTITUTIONS].keys():
            log.failure("Sub-field missing in substitutions field: " + field)

    for applier in APPLIERS:
        for field in applier.required:
            if field not in config[CONFIG_SUBSTITUTIONS].keys():
                log.failure(
                    f"Field missing for applier {log.BLUE}{applier.name}{log.NORMAL}: {log.RED}{field}")


def expand(config):
    for expansion in __EXPANSIONS:
        expansion.expand(config, EXPANSION_DATA)


def apply_defaults(config: Dict, lite_mode: bool) -> None:
    config[CONFIG_SUBSTITUTIONS][DOTFILES_LITE_MODE_KEY] = str(
        lite_mode).lower()
    for key, value in __DEFAULT_FIELDS.items():
        if key not in config[CONFIG_SUBSTITUTIONS]:
            config[CONFIG_SUBSTITUTIONS][key] = value


def apply_preset(config: Dict, preset_name: str) -> None:
    if preset_name not in __PRESETS:
        log.failure(f"Preset {preset_name} does not exist")

    for key, value in __PRESETS[preset_name].items():
        if key not in config[CONFIG_SUBSTITUTIONS]:
            config[CONFIG_SUBSTITUTIONS][key] = value


def initialize(config: Dict):
    if CONFIG_SUBSTITUTIONS not in config:
        config[CONFIG_SUBSTITUTIONS] = {}
