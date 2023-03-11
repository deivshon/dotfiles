import setup.lib.utils as utils

def expandColorStyle(colorStyle, data):
    __expand_efy(colorStyle, data)

def __expand_efy(colorStyle, data):
    mainColor = colorStyle["substitutions"]["mainColor"]
    
    efyFields = data["expansion-data"]["enhancer-for-youtube"]
    newFields = {}

    for col in efyFields.keys():
        _, s, v = utils.hex_to_divided_hsv(efyFields[col])
        newFields[col] = utils.apply_hue(s, v, mainColor)    

    for field in newFields:
        if(field not in colorStyle["substitutions"]):
            colorStyle["substitutions"][field] = newFields[field]
