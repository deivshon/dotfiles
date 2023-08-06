import json

from typing import List

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


def check(config):
    with open(__CONFIG_FILE, "r") as file:
        expected_data = json.loads(file.read())

    config_keys = config.keys()
    if SUBSTITUTIONS not in config_keys:
        log.failure("Substitutions field missing in config")

    for field in expected_data:
        if field not in config_keys:
            log.failure("Field missing in config: " + field)

    for field in EXPECTED_SUBSTITUTIONS:
        if field not in config[SUBSTITUTIONS].keys():
            log.failure("Sub-field missing in substitutions field: " + field)


def expand(config):
    for expansion in __EXPANSIONS:
        expansion.expand(config, EXPANSION_DATA)
