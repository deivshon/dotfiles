from typing import Tuple
from functools import lru_cache
from colorsys import rgb_to_hsv, hsv_to_rgb


@lru_cache(maxsize=512)
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    base = 0 if not hex_color.startswith("#") else 1
    return int(hex_color[base:base + 2], 16), int(hex_color[base + 2:base + 4], 16), int(hex_color[base + 4:base + 6], 16)


@lru_cache(maxsize=512)
def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


@lru_cache(maxsize=512)
def hex_to_hsv(hex_color: str):
    return rgb_to_hsv(*hex_to_rgb(hex_color))


@lru_cache(maxsize=512)
def hsv_to_hex(h: int, s: int, v: int):
    r, g, b = hsv_to_rgb(h, s, v)
    return rgb_to_hex(round(r), round(g), round(b))


@lru_cache(maxsize=512)
def hex_to_divided_hsv(hex):
    hsv = rgb_to_hsv(*hex_to_rgb(hex))
    return hsv[0], hsv[1], hsv[2]


@lru_cache(maxsize=512)
def apply_hue_saturation(v, color):
    hsv = hex_to_hsv(color)
    h, s = hsv[0], hsv[1]
    return hsv_to_hex(h, s, v)
