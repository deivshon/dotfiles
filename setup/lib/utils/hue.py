from matplotlib.colors import hex2color, hsv_to_rgb, rgb_to_hsv, rgb2hex


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
