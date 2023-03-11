import sys
import json

import setup.lib.utils as utils

def check(style):
    with open("setup/data/styleFields.json", "r") as f:
        expectedFields = json.loads(f.read())

    # Check the selected color style contains all the needed fields
    colorStyleKeys = style.keys()
    if "substitutions" not in colorStyleKeys:
        sys.exit("Substitutions field missing in color style")

    for field in expectedFields["other"]:
        if field not in colorStyleKeys:
            sys.exit("Field missing in color style: " + field)

    for field in expectedFields["substitutions"] + expectedFields["setup-expanded-substitutions"]:
        if field not in style["substitutions"].keys():
            sys.exit("Sub-field missing in substitutions field: " + field)

def expand(colorStyle):
    with open("setup/data/expansions.json") as f:
        expansionData = json.loads(f.read())

    __expand_efy(colorStyle, expansionData["enhancer-for-youtube"])

def __expand_efy(colorStyle, efyFields):
    mainColor = colorStyle["substitutions"]["mainColor"]
    newFields = {}

    for col in efyFields.keys():
        _, s, v = utils.hex_to_divided_hsv(efyFields[col])
        newFields[col] = utils.apply_hue(s, v, mainColor)    

    for field in newFields:
        if(field not in colorStyle["substitutions"]):
            colorStyle["substitutions"][field] = newFields[field]
