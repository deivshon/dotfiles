from functools import lru_cache

from matplotlib.colors import hex2color, hsv_to_rgb, rgb_to_hsv, rgb2hex


@lru_cache
def hex_to_hsv(hex):
    return rgb_to_hsv(hex2color(hex))


@lru_cache
def hsv_to_hex(hsv):
    return rgb2hex(hsv_to_rgb(hsv))


@lru_cache
def hex_to_divided_hsv(hex):
    hsv = rgb_to_hsv(hex2color(hex))
    return hsv[0], hsv[1], hsv[2]


@lru_cache
def apply_hue_saturation(v, color):
    hsv = hex_to_hsv(color)
    h, s = hsv[0], hsv[1]
    return hsv_to_hex((h, s, v))
