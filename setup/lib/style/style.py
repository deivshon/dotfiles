import sys
import json

from setup.lib import LIB_DIR
from setup.lib.style import SUBSTITUTIONS, EXPANDED_SUBSTITUTIONS
from setup.lib.style.expansion import EXPANSIONS_FILE, EFY, FIREFOX, SWAYLOCK
from setup.lib.style.expansion import efy, wallpaper, colors_no_hash, firefox, swaylock

__STYLE_FILE = f"{LIB_DIR}/../data/styleFields.json"


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
    with open(EXPANSIONS_FILE) as f:
        expansionData = json.loads(f.read())

    efy.expand(colorStyle, expansionData[EFY])

    wallpaper.expand(colorStyle)

    colors_no_hash.expand(colorStyle)

    firefox.expand(colorStyle, expansionData[FIREFOX])

    swaylock.expand(colorStyle, expansionData[SWAYLOCK])
