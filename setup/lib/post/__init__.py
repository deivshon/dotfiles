import os

from setup.lib import LIB_DIR

DEFAULT_XINITRC = "/etc/X11/xinit/xinitrc"
XINITRC_APPEND = f"{LIB_DIR}/../../dots/.xinitrc_append"
USER_XINITRC = os.path.expanduser("~/.xinitrc")
USER_HYPRSETUP = os.path.expanduser("~/.config/hypr/hyprsetup.conf")
DEVICE_BASHRC = os.path.expanduser("~/.bashrc_device")
DEVICE_BASH_PROFILE = os.path.expanduser("~/.bash_profile_device")
STARTUP_SCRIPT = os.path.expanduser("~/startup/startup.sh")
