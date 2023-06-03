from setup.lib.style.expansion import expand_hue, EFY
from setup.lib.style.expansion.handler import ExpansionHandler


class EfyColors(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        expand_hue(color_data, expansion_data[EFY])
