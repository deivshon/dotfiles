import os
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
__GTK_SETTINGS_FILE = "settings.ini"

__GTK_SETTINGS_SECTION = "Settings"
__GTK_SETTINGS_THEME = "gtk-theme-name"
__GTK_SETTINGS_ICONS = "gtk-icon-theme-name"


def __gtk_applier(config_substitutions: Dict) -> None:
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

    config_theme = config_substitutions[__GTK_THEME]
    config_icons = config_substitutions[__GTK_ICONS]
    current_theme: Optional[str] = None
    current_icons: Optional[str] = None
    if __GTK_SETTINGS_THEME in config[__GTK_SETTINGS_SECTION]:
        current_theme = config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_THEME]
    if __GTK_SETTINGS_ICONS in config[__GTK_SETTINGS_SECTION]:
        current_icons = config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_ICONS]

    if current_theme != config_theme:
        log.info(f"Applying GTK theme {log.YELLOW}{config_theme}")
        config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_THEME] = config_theme
    if current_icons != config_icons:
        log.info(f"Applying GTK icons {log.YELLOW}{config_icons}")
        config[__GTK_SETTINGS_SECTION][__GTK_SETTINGS_ICONS] = config_icons

    with open(settings_file, "w") as f:
        config.write(f)


GTK_APPLIER = Applier(name="gtk", run=__gtk_applier,
                      apply_once=False, required=__GTK_REQUIRED)
