import os
import hashlib
from matplotlib.colors import hex2color, hsv_to_rgb, rgb_to_hsv, rgb2hex


def whitelistChars(string, whitelist):
    return ''.join([char for char in string if char in whitelist])


def hex_to_hsv(hex):
    return rgb_to_hsv(hex2color(hex))


def hsv_to_hex(hsv):
    return rgb2hex(hsv_to_rgb(hsv))


def hex_to_divided_hsv(hex):
    hsv = rgb_to_hsv(hex2color(hex))
    return hsv[0], hsv[1], hsv[2]


def apply_hue(s, v, color):
    h = hex_to_hsv(color)[0]
    return hsv_to_hex((h, s, v))


def get_last_node(path):
    return path[::-1][0:path[::-1].index("/")][::-1]


def get_wallpaper_path(wallpaperName):
    return f"{os.path.expanduser('~')}/Pictures/{wallpaperName}"


def sed_escape_path(str):
    # "\x5c/" = "\/", to avoid unnecessary warning
    return str.replace("/", "\x5c/")


def sha256_checksum(filepath):
    hashHandler = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hashHandler.update(chunk)

    return hashHandler.hexdigest()
