import os
import subprocess

from setup.lib import utils
from setup.lib.utils import process
from setup.lib.post.handler import PostOperationsHandler


class WallpaperPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "wallpaper"

    @classmethod
    def _trigger_impl(cls, color_style):
        user = os.path.expanduser("~")

        wallpaper_path = utils.path.get_wallpaper_path(
            color_style["wallpaperName"])

        if not os.path.isdir(os.path.dirname(wallpaper_path)):
            os.makedirs(os.path.dirname(wallpaper_path))

        if not os.path.isfile(wallpaper_path):
            process.exec(
                ["wget", color_style["wallpaperLink"], "-O", wallpaper_path])

        subprocess.run(["cp", wallpaper_path, user + "/Pictures/wallpaper"])
