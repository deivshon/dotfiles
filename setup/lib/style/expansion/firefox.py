from setup.lib.style.expansion import expand_hue, FIREFOX
from setup.lib.style.expansion.handler import ExpansionHandler


class FirefoxColors(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        expand_hue(color_data, expansion_data[FIREFOX])
