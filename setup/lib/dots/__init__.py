import os
import time

from typing import Set
from dataclasses import dataclass

from setup.lib import LIB_DIR
from setup.lib import log, utils
from setup.lib.dots.targets.firefox import FirefoxVariableTarget


BINARY_DOT_LINKS_FILE = f"{LIB_DIR}/../data/binary_links.json"
SUBSTITUTIONS_DIR = "./substitutions"
DOTFILES_DIR = f"{LIB_DIR}/../../dots"

_FIREFOX = "firefox-userchrome"
TARGET_SEARCH = {
    _FIREFOX: FirefoxVariableTarget()
}
