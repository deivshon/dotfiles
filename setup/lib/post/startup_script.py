import os
import stat

from setup.lib import log
from setup.lib.post import STARTUP_SCRIPT
from setup.lib.post.handler import PostOperationsHandler


class StatusScriptsPostOperations(PostOperationsHandler):
    @staticmethod
    def name() -> str:
        return "status-scripts"

    @classmethod
    def _trigger_impl(cls, _):
        # Create the startup folder and script in the home directory
        # This script is ran every time the X server starts
        if not os.path.isdir(os.path.dirname(STARTUP_SCRIPT)):
            os.makedirs(os.path.dirname(STARTUP_SCRIPT))

        if not os.path.isfile(STARTUP_SCRIPT):
            with open(STARTUP_SCRIPT, "w") as file:
                file.write("#!/bin/sh\n")

            # This line is the equivalent of chmod +x ~/startup/startup.sh
            os.chmod(STARTUP_SCRIPT, os.stat(
                STARTUP_SCRIPT).st_mode | stat.S_IEXEC)
        else:
            log.info(
                f"{log.RED}{STARTUP_SCRIPT} already exists{log.NORMAL}")
