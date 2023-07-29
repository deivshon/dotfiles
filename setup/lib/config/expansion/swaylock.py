from setup.lib.config.expansion import expand_hue, SWAYLOCK
from setup.lib.config.expansion.handler import ExpansionHandler


class SwayLockColors(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        expand_hue(color_data, expansion_data[SWAYLOCK])
