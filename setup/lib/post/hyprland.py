import os

from setup.lib.post import USER_HYPRSETUP


def trigger():
    if not os.path.isfile(USER_HYPRSETUP):
        with open(USER_HYPRSETUP, "w") as f:
            f.write("# Device specific Hyprland options\n")
