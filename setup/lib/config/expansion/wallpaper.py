from setup.lib import utils
from setup.lib.const.config import CONFIG_SUBSTITUTIONS
from setup.lib.config.expansion.handler import ExpansionHandler


class WallpaperPath(ExpansionHandler):
    @staticmethod
    def expand(color_data, _):
        color_data[CONFIG_SUBSTITUTIONS]["wallpaper-path"] = utils.path.get_wallpaper_path(
            color_data["wallpaper-name"])
