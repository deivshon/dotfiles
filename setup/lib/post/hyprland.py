import os

from setup.lib.post import USER_HYPRSETUP
from setup.lib.post.handler import PostOperationsHandler


class HyprlandPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "hyprland"

    @classmethod
    def _trigger_impl(cls, color_style):
        if not os.path.isfile(USER_HYPRSETUP):
            with open(USER_HYPRSETUP, "w") as f:
                f.write("# Device specific Hyprland options\n")
