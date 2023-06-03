import sys
import json

from typing import List, Tuple, Any

from setup.lib import LIB_DIR
from setup.lib.style import SUBSTITUTIONS, EXPANDED_SUBSTITUTIONS
from setup.lib.style.expansion import EXPANSION_DATA, EFY, FIREFOX, SWAYLOCK
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


def check(style):
    with open(__STYLE_FILE, "r") as f:
        expectedFields = json.loads(f.read())

    # Check the selected color style contains all the needed fields
    colorStyleKeys = style.keys()
    if SUBSTITUTIONS not in colorStyleKeys:
        sys.exit("Substitutions field missing in color style")

    for field in expectedFields["other"]:
        if field not in colorStyleKeys:
            sys.exit("Field missing in color style: " + field)

    for field in expectedFields[SUBSTITUTIONS] + expectedFields[EXPANDED_SUBSTITUTIONS]:
        if field not in style[SUBSTITUTIONS].keys():
            sys.exit("Sub-field missing in substitutions field: " + field)


def expand(colorStyle):
    for expansion in __EXPANSIONS:
        expansion.expand(colorStyle, EXPANSION_DATA)
