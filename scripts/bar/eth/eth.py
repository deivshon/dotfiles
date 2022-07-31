#!/bin/python3

import os
import sys

label = "ETH "
suffix = "|" if "--separator" in sys.argv else ""

for interface in os.listdir("/sys/class/net/"):
    if "enp" in interface or "eth" in interface:
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        isUp = stateFile.read().strip() == "up"

        if not isUp:
            quit()
        else:
            print(label + "UP" + suffix)
        quit()
