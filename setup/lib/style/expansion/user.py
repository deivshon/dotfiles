import os

from setup.lib.style import SUBSTITUTIONS
from setup.lib.style.expansion.handler import ExpansionHandler


class SetupUser(ExpansionHandler):
    __SETUP_USER_KEY = "setupUser"

    @staticmethod
    def expand(color_data, _):
        color_data[SUBSTITUTIONS][SetupUser.__SETUP_USER_KEY] = os.getlogin()
