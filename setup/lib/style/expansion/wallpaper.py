from setup.lib.style import SUBSTITUTIONS
from setup.lib import utils as genutils
from setup.lib.style.expansion.handler import ExpansionHandler


class WallpaperPath(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        color_data[SUBSTITUTIONS]["wallpaperPath"] = genutils.sed_escape_path(
            genutils.get_wallpaper_path(color_data["wallpaperName"])
        )
