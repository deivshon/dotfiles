import os

from setup.lib.post import DEVICE_BASHRC, DEVICE_BASH_PROFILE


def trigger():
    if not os.path.isfile(DEVICE_BASHRC):
        with open(DEVICE_BASHRC, "w") as f:
            f.write("#!/bin/bash\n\n# Device specific bashrc\n")

    if not os.path.isfile(DEVICE_BASH_PROFILE):
        with open(DEVICE_BASH_PROFILE, "w") as f:
            f.write("#!/bin/bash\n\n# Device specific bash_profile\n")
