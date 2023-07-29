import os

from setup.lib.config import SUBSTITUTIONS
from setup.lib.config.expansion.handler import ExpansionHandler


class SetupUser(ExpansionHandler):
    __SETUP_USER_KEY = "setup-user"

    @staticmethod
    def expand(color_data, _):
        color_data[SUBSTITUTIONS][SetupUser.__SETUP_USER_KEY] = os.getlogin()
