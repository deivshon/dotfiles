import setup.lib.printing as printing

from setup.lib.post import USER_XINITRC, STARTUP_SCRIPT, USER_HYPRSETUP, DEVICE_BASHRC, DEVICE_BASH_PROFILE
from setup.lib.post import wallpaper
from setup.lib.post import xinitrc
from setup.lib.post import startup_script
from setup.lib.post import rustup
from setup.lib.post import reflector
from setup.lib.post import hyprland
from setup.lib.post import bash


def install():
    # To be called only the first time the setup is run
    printing.colorPrint(
        "Starting post install operations...", printing.MAGENTA)

    xinitrc.trigger()
    printing.colorPrint(f"{USER_XINITRC} handled", printing.WHITE)

    startup_script.trigger()
    printing.colorPrint(f"{STARTUP_SCRIPT} handled", printing.WHITE)

    rustup.trigger()
    printing.colorPrint("Rustup handled", printing.WHITE)

    reflector.trigger()
    printing.colorPrint("Reflector handled", printing.WHITE)

    hyprland.trigger()
    printing.colorPrint(f"{USER_HYPRSETUP} handled", printing.WHITE)

    bash.trigger()
    printing.colorPrint(f"Bash handled", printing.WHITE)

    printing.colorPrint("Ended post install operations...", printing.GREEN)


def change(colorStyle):
    # To be called every time the setup is run
    printing.colorPrint("Starting post run operations...", printing.MAGENTA)

    wallpaper.trigger(colorStyle)
    printing.colorPrint("Wallpaper handled", printing.WHITE)

    printing.colorPrint("Ended post run operations...", printing.GREEN)
