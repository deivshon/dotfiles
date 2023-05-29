import sys

from setup.lib import LIB_DIR
from setup.lib.style import SUBSTITUTIONS, MAIN_COLOR
from setup.lib import utils as genutils

EXPANSIONS_FILE = f"{LIB_DIR}/../data/expansions.json"

EFY = "enhancer-for-youtube"
FIREFOX = "firefox"
SWAYLOCK = "swaylock"
MAIN_COLOR_NOHASH = "mainColorNoHash"
SECONDARY_COLOR_NOHASH = "secondaryColorNoHash"


def expand_hue(colorStyle, colorFields, baseColor=None):
    if baseColor == None:
        baseColor = colorStyle[SUBSTITUTIONS][MAIN_COLOR]
    newFields = {}

    for col in colorFields.keys():
        alpha = ""
        if len(colorFields[col]) == 9:
            alpha = colorFields[col][-2:]
            colorFields[col] = colorFields[col][:-2]
        elif len(colorFields[col]) != 7:
            sys.exit(
                f"Malformed hex color passed to hue expansion: {colorFields[col]}")

        _, s, v = genutils.hex_to_divided_hsv(colorFields[col])
        newFields[col] = genutils.apply_hue(s, v, baseColor) + alpha

    for field in newFields:
        if (field not in colorStyle[SUBSTITUTIONS]):
            colorStyle[SUBSTITUTIONS][field] = newFields[field]