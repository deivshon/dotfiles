from setup.lib.style import SUBSTITUTIONS
from setup.lib import utils as genutils


def expand(colorStyle):
    colorStyle[SUBSTITUTIONS]["wallpaperPath"] = genutils.sed_escape_path(
        genutils.get_wallpaper_path(colorStyle["wallpaperName"])
    )
