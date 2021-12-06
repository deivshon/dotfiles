#!/bin/python3

# Outputs the nf-mdi-wifi nerd font char if the wifi is up and nf-mdi-wifi_off otherwise

import os

wirelessInterface = ""

for interface in os.listdir("/sys/class/net/"):
    if(interface.startswith("wlp") or interface.startswith("wlan")):
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        state = stateFile.read().strip()
        print(state)
        if(state == "up"):
            print("直")
        else:
            print("睊")
