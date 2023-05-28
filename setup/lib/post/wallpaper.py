import os
import subprocess

from setup.lib import utils


def trigger(colorStyle):
    user = os.path.expanduser("~")

    wallpaperPath = utils.get_wallpaper_path(colorStyle["wallpaperName"])

    if not os.path.isdir(os.path.dirname(wallpaperPath)):
        utils.make_dirs(os.path.dirname(wallpaperPath))

    if not os.path.isfile(wallpaperPath):
        subprocess.run(
            ["wget", colorStyle["wallpaperLink"], "-O", wallpaperPath])
    subprocess.run(["cp", wallpaperPath, user + "/Pictures/wallpaper"])
