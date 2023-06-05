import json

from setup.lib import log
from setup.lib import LIB_DIR
from setup.lib.style import SUBSTITUTIONS, MAIN_COLOR
from setup.lib import utils as genutils

EXPANSIONS_FILE = f"{LIB_DIR}/../data/expansions.json"

EFY = "enhancer-for-youtube"
FIREFOX = "firefox"
SWAYLOCK = "swaylock"
MAIN_COLOR_NOHASH = "mainColorNoHash"
SECONDARY_COLOR_NOHASH = "secondaryColorNoHash"

with open(EXPANSIONS_FILE) as file:
    EXPANSION_DATA = json.loads(file.read())


def expand_hue(color_style, color_fields, base_color=None):
    if base_color is None:
        base_color = color_style[SUBSTITUTIONS][MAIN_COLOR]
    new_fields = {}

    for col in color_fields.keys():
        alpha = ""
        if len(color_fields[col]) == 9:
            alpha = color_fields[col][-2:]
            color_fields[col] = color_fields[col][:-2]
        elif len(color_fields[col]) != 7:
            log.failure(
                f"Malformed hex color passed to hue expansion: {color_fields[col]}")

        _, s, v = genutils.hue.hex_to_divided_hsv(color_fields[col])
        new_fields[col] = genutils.hue.apply_hue(s, v, base_color) + alpha

    for field, value in new_fields.items():
        if field not in color_style[SUBSTITUTIONS]:
            color_style[SUBSTITUTIONS][field] = value
