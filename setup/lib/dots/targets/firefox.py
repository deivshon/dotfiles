import os

from typing import List

from setup.lib.dots.targets.handler import VariableTargetHandler


class FirefoxVariableTarget(VariableTargetHandler):
    @staticmethod
    def get_targets() -> List:
        if not os.path.isdir(os.path.expanduser("~/.mozilla")):
            return []

        if not os.path.isdir(os.path.expanduser("~/.mozilla/firefox")):
            return []

        targets = []
        for path in os.listdir(os.path.expanduser("~/.mozilla/firefox")):
            if ".default" in path:
                targets.append(
                    f"{os.path.expanduser('~/.mozilla/firefox')}/{path}/chrome/userChrome.css")

        return targets
