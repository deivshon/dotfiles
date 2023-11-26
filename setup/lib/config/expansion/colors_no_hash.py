from setup.lib.config.expansion.handler import ExpansionHandler
from setup.lib.config.expansion import MAIN_COLOR_NOHASH, SECONDARY_COLOR_NOHASH
from setup.lib.const.config import MAIN_COLOR, SECONDARY_COLOR, CONFIG_SUBSTITUTIONS


class ColorsNoHash(ExpansionHandler):
    @staticmethod
    def expand(color_data, _):
        color_data[CONFIG_SUBSTITUTIONS][MAIN_COLOR_NOHASH] = color_data[CONFIG_SUBSTITUTIONS][MAIN_COLOR][1:]
        color_data[CONFIG_SUBSTITUTIONS][SECONDARY_COLOR_NOHASH] = color_data[CONFIG_SUBSTITUTIONS][SECONDARY_COLOR][1:]
