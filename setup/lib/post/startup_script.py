import os

from os import stat

from setup.lib import utils
from setup.lib import printing
from setup.lib.post import STARTUP_SCRIPT


def trigger():
    # Create the startup folder and script in the home directory
    # This script is ran every time the X server starts
    utils.make_dirs(os.path.dirname(STARTUP_SCRIPT))

    if not os.path.isfile(STARTUP_SCRIPT):
        with open(STARTUP_SCRIPT, "w") as f:
            f.write("#!/bin/sh\n")

        # This line is the equivalent of chmod +x ~/startup/startup.sh
        os.chmod(STARTUP_SCRIPT, os.stat(
            STARTUP_SCRIPT).st_mode | stat.S_IEXEC)
    else:
        printing.colorPrint(f"{STARTUP_SCRIPT} already exists", printing.RED)
