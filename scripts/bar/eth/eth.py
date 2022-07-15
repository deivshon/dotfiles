#!/bin/python3

import os
import sys

label = "ETH "
suffix = "|" if "--separator" in sys.argv else ""

for interface in os.listdir("/sys/class/net/"):
    if "enp" in interface or "eth" in interface:
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        status = "UP" if stateFile.read().strip() == "up" else "DOWN"

        print(label + status + suffix)
        quit()
