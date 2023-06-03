from setup.lib.style.expansion import expand_hue, SWAYLOCK
from setup.lib.style.expansion.handler import ExpansionHandler


class SwayLockColors(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        expand_hue(color_data, expansion_data[SWAYLOCK])
