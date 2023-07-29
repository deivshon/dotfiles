from setup.lib.config import SUBSTITUTIONS, MAIN_COLOR, SECONDARY_COLOR
from setup.lib.config.expansion import MAIN_COLOR_NOHASH, SECONDARY_COLOR_NOHASH
from setup.lib.config.expansion.handler import ExpansionHandler


class ColorsNoHash(ExpansionHandler):
    @staticmethod
    def expand(color_data, _):
        color_data[SUBSTITUTIONS][MAIN_COLOR_NOHASH] = color_data[SUBSTITUTIONS][MAIN_COLOR][1:]
        color_data[SUBSTITUTIONS][SECONDARY_COLOR_NOHASH] = color_data[SUBSTITUTIONS][SECONDARY_COLOR][1:]
