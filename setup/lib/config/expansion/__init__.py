import json
from typing import Tuple

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.const.config import MAIN_COLOR, CONFIG_SUBSTITUTIONS

EXPANSIONS_FILE = f"{LIB_DIR}/../data/expansions.json"

EFY = "enhancer-for-youtube"
FIREFOX = "firefox"
SWAYLOCK = "swaylock"
MAIN_COLOR_NOHASH = "main-color-no-hash"
SECONDARY_COLOR_NOHASH = "secondary-color-no-hash"

with open(EXPANSIONS_FILE) as file:
    EXPANSION_DATA = json.loads(file.read())


def expand_hue(config, color_fields, base_color=None):
    if base_color is None:
        base_color = config[CONFIG_SUBSTITUTIONS][MAIN_COLOR]
    new_fields = {}

    for field, color in color_fields.items():
        if color.startswith("#FFFFFF"):
            new_fields[field] = color
            continue

        alpha, color = __remove_alpha(color)
        _, _, v = utils.hue.hex_to_divided_hsv(color)
        new_fields[field] = utils.hue.apply_hue_saturation(
            v, base_color) + alpha

    for field, value in new_fields.items():
        if field not in config[CONFIG_SUBSTITUTIONS]:
            config[CONFIG_SUBSTITUTIONS][field] = value


def __remove_alpha(color: str) -> Tuple[str, str]:
    if len(color) == 9:
        alpha = color[-2:]
        color = color[:-2]
        return alpha, color
    elif len(color) != 7:
        log.failure(
            f"Malformed hex color passed to hue expansion: {color}")
    else:
        return "", color
