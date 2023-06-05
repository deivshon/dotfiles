import sys
import json

from typing import List

from setup.lib import LIB_DIR
from setup.lib.style import SUBSTITUTIONS, EXPECTED_SUBSTITUTIONS
from setup.lib.style.expansion import EXPANSION_DATA
from setup.lib.style.expansion.handler import ExpansionHandler
from setup.lib.style.expansion.efy import EfyColors
from setup.lib.style.expansion.wallpaper import WallpaperPath
from setup.lib.style.expansion.colors_no_hash import ColorsNoHash
from setup.lib.style.expansion.firefox import FirefoxColors
from setup.lib.style.expansion.swaylock import SwayLockColors

__STYLE_FILE = f"{LIB_DIR}/../data/styleFields.json"

__EXPANSIONS: List[ExpansionHandler] = [
    EfyColors(),
    WallpaperPath(),
    ColorsNoHash(),
    FirefoxColors(),
    SwayLockColors()
]


def check(color_style):
    with open(__STYLE_FILE, "r") as file:
        expected_data = json.loads(file.read())

    color_style_keys = color_style.keys()
    if SUBSTITUTIONS not in color_style_keys:
        sys.exit("Substitutions field missing in color style")

    for field in expected_data:
        if field not in color_style_keys:
            sys.exit("Field missing in color style: " + field)

    for field in EXPECTED_SUBSTITUTIONS:
        if field not in color_style[SUBSTITUTIONS].keys():
            sys.exit("Sub-field missing in substitutions field: " + field)


def expand(color_style):
    for expansion in __EXPANSIONS:
        expansion.expand(color_style, EXPANSION_DATA)
