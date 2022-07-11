#!/bin/python3

import os

for interface in os.listdir("/sys/class/net/"):
    if "enp" in interface or "eth" in interface:
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        status = "UP" if stateFile.read().strip() == "up" else "DOWN"

        print(status)
        quit()
