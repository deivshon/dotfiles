from setup.lib.style import SUBSTITUTIONS, MAIN_COLOR, SECONDARY_COLOR
from setup.lib.style.expansion import MAIN_COLOR_NOHASH, SECONDARY_COLOR_NOHASH
from setup.lib.style.expansion.handler import ExpansionHandler


class ColorsNoHash(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        color_data[SUBSTITUTIONS][MAIN_COLOR_NOHASH] = color_data[SUBSTITUTIONS][MAIN_COLOR][1:]
        color_data[SUBSTITUTIONS][SECONDARY_COLOR_NOHASH] = color_data[SUBSTITUTIONS][SECONDARY_COLOR][1:]
