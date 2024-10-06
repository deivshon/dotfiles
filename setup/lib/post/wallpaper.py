import os

from setup.lib import utils
from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class WallpaperPostOperations(PostOperationsHandler):
    __WALLPAPER_LINK_KEY = "wallpaper-link"

    @staticmethod
    def name() -> str:
        return "wallpaper"

    @staticmethod
    def needed_in_lite() -> bool:
        return True

    @classmethod
    def _trigger_impl(cls, config):
        wallpaper_path = utils.path.get_wallpaper_path(
            config["wallpaper-name"])

        if not os.path.isdir(os.path.dirname(wallpaper_path)):
            os.makedirs(os.path.dirname(wallpaper_path))

        if not os.path.isfile(wallpaper_path):
            process.exec(
                ["wget", config[cls.__WALLPAPER_LINK_KEY], "-O", wallpaper_path])
