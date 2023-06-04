from setup.lib.style import SUBSTITUTIONS
from setup.lib import utils
from setup.lib.style.expansion.handler import ExpansionHandler


class WallpaperPath(ExpansionHandler):
    @staticmethod
    def expand(color_data, expansion_data):
        color_data[SUBSTITUTIONS]["wallpaperPath"] = utils.path.sed_escape_path(
            utils.path.get_wallpaper_path(color_data["wallpaperName"])
        )
