import sys
import json

import setup.lib.utils as utils

from setup.lib import LIB_DIR

__STYLE_FILE = f"{LIB_DIR}/../data/styleFields.json"
__EXPANSIONS_FILE = f"{LIB_DIR}/../data/expansions.json"
__SUBSTITUTIONS = "substitutions"
__EXPANDED_SUBSTITUTIONS = "setup-expanded-substitutions"

__EFY = "enhancer-for-youtube"
__FIREFOX = "firefox"
__SWAYLOCK = "swaylock"
__MAIN_COLOR = "mainColor"
__SECONDARY_COLOR = "secondaryColor"
__MAIN_COLOR_NOHASH = "mainColorNoHash"
__SECONDARY_COLOR_NOHASH = "secondaryColorNoHash"


def check(style):
    with open(__STYLE_FILE, "r") as f:
        expectedFields = json.loads(f.read())

    # Check the selected color style contains all the needed fields
    colorStyleKeys = style.keys()
    if __SUBSTITUTIONS not in colorStyleKeys:
        sys.exit("Substitutions field missing in color style")

    for field in expectedFields["other"]:
        if field not in colorStyleKeys:
            sys.exit("Field missing in color style: " + field)

    for field in expectedFields[__SUBSTITUTIONS] + expectedFields[__EXPANDED_SUBSTITUTIONS]:
        if field not in style[__SUBSTITUTIONS].keys():
            sys.exit("Sub-field missing in substitutions field: " + field)


def expand(colorStyle):
    with open(__EXPANSIONS_FILE) as f:
        expansionData = json.loads(f.read())

    __expand_efy(colorStyle, expansionData[__EFY])

    __expand_wallpaper(colorStyle)

    __expand_colors_no_hash(colorStyle)

    __expand_firefox(colorStyle, expansionData[__FIREFOX])

    __expand_swaylock(colorStyle, expansionData[__SWAYLOCK])


def __expand_wallpaper(colorStyle):
    colorStyle[__SUBSTITUTIONS]["wallpaperPath"] = utils.sed_escape_path(
        utils.get_wallpaper_path(colorStyle["wallpaperName"])
    )


def __expand_colors_no_hash(colorStyle):
    colorStyle[__SUBSTITUTIONS][__MAIN_COLOR_NOHASH] = colorStyle[__SUBSTITUTIONS][__MAIN_COLOR][1:]
    colorStyle[__SUBSTITUTIONS][__SECONDARY_COLOR_NOHASH] = colorStyle[__SUBSTITUTIONS][__SECONDARY_COLOR][1:]


def __expand_hue(colorStyle, colorFields, baseColor=None):
    if baseColor == None:
        baseColor = colorStyle[__SUBSTITUTIONS][__MAIN_COLOR]
    newFields = {}

    for col in colorFields.keys():
        alpha = ""
        if len(colorFields[col]) == 9:
            alpha = colorFields[col][-2:]
            colorFields[col] = colorFields[col][:-2]
        elif len(colorFields[col]) != 7:
            sys.exit(
                f"Malformed hex color passed to hue expansion: {colorFields[col]}")

        _, s, v = utils.hex_to_divided_hsv(colorFields[col])
        newFields[col] = utils.apply_hue(s, v, baseColor) + alpha

    for field in newFields:
        if (field not in colorStyle[__SUBSTITUTIONS]):
            colorStyle[__SUBSTITUTIONS][field] = newFields[field]


def __expand_efy(colorStyle, efyFields):
    __expand_hue(colorStyle, efyFields)


def __expand_firefox(colorStyle, firefoxFields):
    __expand_hue(colorStyle, firefoxFields)


def __expand_swaylock(colorStyle, swayFields):
    __expand_hue(colorStyle, swayFields)
