import os
import subprocess

import configparser

from typing import Dict, List, Optional

from setup.lib import log
from setup.lib.dots.appliers.applier import Applier
from setup.lib.utils import HOME_DIR

__GTK_THEME = "gtk-theme"
__GTK_ICONS = "gtk-icon-theme"
__GTK_REQUIRED: List[str] = [
    __GTK_THEME,
    __GTK_ICONS
]

__GTK_SETTINGS_FILE = os.path.join(
    HOME_DIR, ".config", "gtk-3.0", "settings.ini")
__GTK_XSETTINGS_FILE = os.path.join(
    HOME_DIR, ".config", "xsettingsd", "xsettingsd.conf")

__GTK_SETTINGS_SECTION = "Settings"
__GTK_SETTINGS_THEME = "gtk-theme-name"
__GTK_SETTINGS_ICONS = "gtk-icon-theme-name"

__GSETTINGS_GTK_THEME = "gtk-theme"
__GSETTINGS_GTK_ICONS = "icon-theme"


def __gsetting_cmd(setting: str, value: str) -> Optional[Exception]:
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", setting, value], capture_output=True)
    except Exception as e:
        return e


def __apply_gtk(config_theme: str, config_icons: str) -> None:
    if not os.path.isfile(__GTK_SETTINGS_FILE):
        log.error(
            f"Could not find GTK settings file: {log.RED}{__GTK_SETTINGS_FILE}{log.NORMAL} does not exist")
        return

    config = configparser.ConfigParser()
    read_ok = config.read(__GTK_SETTINGS_FILE)
    if len(read_ok) == 0:
        log.error(
            f"Could not read GTK settings at {log.RED}{__GTK_SETTINGS_FILE}")
        return

    if __GTK_SETTINGS_SECTION not in config:
        log.error(
            f"Could not find settings section in settings at {log.RED}{__GTK_SETTINGS_FILE}")
        return

    log.info(
        f"Applying GTK theme {log.YELLOW}{config_theme}{log.NORMAL} ({__GTK_SETTINGS_FILE})")
    config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_THEME] = config_theme
    log.info(
        f"Applying GTK icons {log.YELLOW}{config_icons}{log.NORMAL} ({__GTK_SETTINGS_FILE})")
    config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_ICONS] = config_icons

    with open(__GTK_SETTINGS_FILE, "w") as f:
        config.write(f)


def __apply_gtk_wayland(config_theme: str, config_icons: str) -> None:
    theme_setting_err = __gsetting_cmd(__GSETTINGS_GTK_THEME, config_theme)
    icons_setting_err = __gsetting_cmd(__GSETTINGS_GTK_ICONS, config_icons)
    if theme_setting_err is not None:
        log.error(
            f"Could not apply GTK theme: {log.RED}{theme_setting_err}{log.NORMAL} (gsettings)")
    else:
        log.info(
            f"Applying GTK theme {log.YELLOW}{config_theme}{log.NORMAL} (gsettings)")
    if icons_setting_err is not None:
        log.error(
            f"Could not apply GTK icons theme with gsettings: {log.RED}{icons_setting_err}{log.NORMAL} (gsettings)")
    else:
        log.info(
            f"Applying GTK icons {log.YELLOW}{config_icons}{log.NORMAL} (gsettings)")


def __apply_gtk_xwayland(config_theme: str, config_icons: str) -> None:
    if not os.path.isfile(__GTK_XSETTINGS_FILE):
        log.error(
            f"Could not find GTK xsettings file at {log.RED}{__GTK_XSETTINGS_FILE}")
        return

    log.info(
        f"Applying GTK theme {log.YELLOW}{config_theme}{log.NORMAL} ({__GTK_XSETTINGS_FILE})")
    subprocess.run(["sed", "-iE", "s/Net\\/ThemeName .*/" +
                   f"Net\\/ThemeName {config_theme}" + "/g", __GTK_XSETTINGS_FILE])
    log.info(
        f"Applying GTK icons {log.YELLOW}{config_icons}{log.NORMAL} ({__GTK_XSETTINGS_FILE})")
    subprocess.run(["sed", "-iE", "s/Net\\/IconThemeName .*/" +
                   f"Net\\/IconThemeName {config_icons}" + "/g", __GTK_XSETTINGS_FILE])


def __gtk_applier(config_substitutions: Dict) -> None:
    config_theme = config_substitutions[__GTK_THEME]
    config_icons = config_substitutions[__GTK_ICONS]

    __apply_gtk(config_theme, config_icons)
    __apply_gtk_wayland(config_theme, config_icons)
    __apply_gtk_xwayland(config_theme, config_icons)


GTK_APPLIER = Applier(name="gtk", run=__gtk_applier,
                      apply_once=False, required=__GTK_REQUIRED)
