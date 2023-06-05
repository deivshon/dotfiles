import os


def get_last_node(path):
    return path[::-1][0:path[::-1].index("/")][::-1]


def get_wallpaper_path(wallpaper_name):
    return f"{os.path.expanduser('~')}/Pictures/{wallpaper_name}"


def sed_escape_path(str):
    # "\x5c/" = "\/", to avoid unnecessary warning
    return str.replace("/", "\x5c/")
