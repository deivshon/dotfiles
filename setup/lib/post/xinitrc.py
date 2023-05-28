import os

from setup.lib import printing
from setup.lib.post import USER_XINITRC, DEFAULT_XINITRC, XINITRC_APPEND


def trigger():
    if os.path.isfile(USER_XINITRC):
        printing.colorPrint(f"{USER_XINITRC} already exists", printing.RED)
        return

    if not os.path.isfile(DEFAULT_XINITRC):
        printing.colorPrint(
            "Couldn't handle xinitrc: default xinitrc not found", printing.RED)
        return

    with open(DEFAULT_XINITRC) as f:
        xinitrc = f.read().splitlines()

    if "twm &" not in xinitrc:
        printing.colorPrint(
            "Couldn't handle xinitrc: malformed default xinitrc", printing.RED)
        return

    xinitrc = xinitrc[0:xinitrc.index("twm &")]

    with open(XINITRC_APPEND, "r") as f:
        xinitrc_append = f.read()

    with open(USER_XINITRC, "w") as f:
        f.write("\n".join(xinitrc) + "\n" + xinitrc_append)
