import os

from setup.lib.post import DEVICE_BASHRC, DEVICE_BASH_PROFILE
from setup.lib.post.handler import PostOperationsHandler


class BashPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "bash"

    @classmethod
    def _trigger_impl(cls, _):
        if not os.path.isfile(DEVICE_BASHRC):
            with open(DEVICE_BASHRC, "w") as file:
                file.write("#!/bin/bash\n\n# Device specific bashrc\n")

        if not os.path.isfile(DEVICE_BASH_PROFILE):
            with open(DEVICE_BASH_PROFILE, "w") as file:
                file.write("#!/bin/bash\n\n# Device specific bash_profile\n")
