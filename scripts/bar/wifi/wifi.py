#!/bin/python3

import os
import sys
import subprocess

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.insert(1, scriptDir + "/../../scriptingUtils")

import scriptingUtils

wirelessInterface = ""
hasIw = False

quality = ""
ssid = ""

for interface in os.listdir("/sys/class/net/"):
    if(interface.startswith("wlp") or interface.startswith("wlan")):
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        isUp = True if stateFile.read().strip() == "up" else False
        if(isUp):
            if(os.path.isfile("/usr/bin/iw")):
                hasIw = True
                iwOutput = subprocess.run(["iw", "dev", interface, "link"], capture_output=True)
                iwOutput = (iwOutput.stdout.decode()).split("\n")
                
                for line in iwOutput:
                    if("dBm" in line):
                        quality = int(scriptingUtils.whitelistChars(line.strip(),"0123456789-"))
                        if(quality > -50):
                            quality = 100
                        elif(quality < -100):
                            quality= 0
                        else:
                            quality = (quality + 100) * 2
                    elif("SSID" in line):
                        ssid = line.strip().removeprefix("SSID: ")

        if(isUp == "down"):
            print("DOWN|")
        elif(isUp and hasIw):
            print(str(quality) + "%", ssid + "|")
        else:
            print("UP|")
        quit()
