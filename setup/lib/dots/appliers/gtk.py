import os
import subprocess

import configparser

from typing import Dict, List, Optional

from setup.lib import log
from setup.lib.dots.appliers.applier import Applier

__GTK_THEME = "gtk-theme"
__GTK_ICONS = "gtk-icon-theme"
__GTK_REQUIRED: List[str] = [
    __GTK_THEME,
    __GTK_ICONS
]

__GTK_CONFIG_DIR: List[str] = [".config", "gtk-3.0"]
__GTK_XSETTINGS_DIR: List[str] = [".config", "xsettingsd"]
__GTK_SETTINGS_FILE = "settings.ini"
__GTK_XSETTINGS_FILE = "xsettingsd.conf"

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
    gtk_dir = os.path.join(os.path.expanduser("~"), *__GTK_CONFIG_DIR)
    if not os.path.isdir(gtk_dir):
        log.error(
            f"Could not find GTK directory: {log.RED}{gtk_dir}{log.NORMAL} does not exist")
        return

    settings_file = os.path.join(gtk_dir, __GTK_SETTINGS_FILE)
    if not os.path.isfile(settings_file):
        log.error(
            f"Could not find GTK settings file: {log.RED}{settings_file}{log.NORMAL} does not exist")
        return

    config = configparser.ConfigParser()
    read_ok = config.read(settings_file)
    if len(read_ok) == 0:
        log.error(f"Could not read GTK settings at {log.RED}{settings_file}")
        return

    if __GTK_SETTINGS_SECTION not in config:
        log.error(
            f"Could not find settings section in settings at {log.RED}{settings_file}")
        return

    log.info(
        f"Applying GTK theme {log.YELLOW}{config_theme}{log.NORMAL} ({settings_file})")
    config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_THEME] = config_theme
    log.info(
        f"Applying GTK icons {log.YELLOW}{config_icons}{log.NORMAL} ({settings_file})")
    config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_ICONS] = config_icons

    with open(settings_file, "w") as f:
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
    xsettings_file = os.path.join(
        os.path.expanduser("~"), *__GTK_XSETTINGS_DIR, __GTK_XSETTINGS_FILE)
    if not os.path.isfile(xsettings_file):
        log.error(
            f"Could not find GTK xsettings file at {log.RED}{xsettings_file}")
        return

    log.info(
        f"Applying GTK theme {log.YELLOW}{config_theme}{log.NORMAL} ({xsettings_file})")
    subprocess.run(["sed", "-iE", "s/Net\\/ThemeName .*/" +
                   f"Net\\/ThemeName {config_theme}" + "/g", xsettings_file])
    log.info(
        f"Applying GTK icons {log.YELLOW}{config_icons}{log.NORMAL} ({xsettings_file})")
    subprocess.run(["sed", "-iE", "s/Net\\/IconThemeName .*/" +
                   f"Net\\/IconThemeName {config_icons}" + "/g", xsettings_file])


def __gtk_applier(config_substitutions: Dict) -> None:
    config_theme = config_substitutions[__GTK_THEME]
    config_icons = config_substitutions[__GTK_ICONS]

    __apply_gtk(config_theme, config_icons)
    __apply_gtk_wayland(config_theme, config_icons)
    __apply_gtk_xwayland(config_theme, config_icons)


GTK_APPLIER = Applier(name="gtk", run=__gtk_applier,
                      apply_once=False, required=__GTK_REQUIRED)
