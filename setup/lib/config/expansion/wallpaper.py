from setup.lib.config import SUBSTITUTIONS
from setup.lib import utils
from setup.lib.config.expansion.handler import ExpansionHandler


class WallpaperPath(ExpansionHandler):
    @staticmethod
    def expand(color_data, _):
        color_data[SUBSTITUTIONS]["wallpaper-path"] = utils.path.get_wallpaper_path(
            color_data["wallpaper-name"])
