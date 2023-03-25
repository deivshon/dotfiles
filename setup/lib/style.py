import sys
import json

import setup.lib.utils as utils

__STYLE_FILE = "./setup/data/styleFields.json"
__EXPANSIONS_FILE = "./setup/data/expansions.json"
__SUBSTITUTIONS = "substitutions"
__EXPANDED_SUBSTITUTIONS = "setup-expanded-substitutions"

__EFY = "enhancer-for-youtube"
__MAIN_COLOR = "mainColor"

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

def __expand_efy(colorStyle, efyFields):
    mainColor = colorStyle[__SUBSTITUTIONS][__MAIN_COLOR]
    newFields = {}

    for col in efyFields.keys():
        _, s, v = utils.hex_to_divided_hsv(efyFields[col])
        newFields[col] = utils.apply_hue(s, v, mainColor)    

    for field in newFields:
        if(field not in colorStyle[__SUBSTITUTIONS]):
            colorStyle[__SUBSTITUTIONS][field] = newFields[field]

def __expand_wallpaper(colorStyle):
    colorStyle[__SUBSTITUTIONS]["wallpaperPath"] = utils.get_wallpaper_path(colorStyle["wallpaperName"])
