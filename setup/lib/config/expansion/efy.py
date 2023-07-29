from setup.lib.config.expansion import expand_hue, EFY
from setup.lib.config.expansion.handler import ExpansionHandler


class EfyColors(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        expand_hue(color_data, expansion_data[EFY])
