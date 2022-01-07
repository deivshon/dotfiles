#!/bin/python3

# Outputs the nf-mdi-wifi nerd font char if the wifi is up, followed by the quality of the signal, and nf-mdi-wifi_off if thw wifi is down

import os
import sys
import subprocess

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.insert(1, scriptDir + "/../../scriptingUtils")

import scriptingUtils

wirelessInterface = ""
icon = "睊"
hasIw = False

quality = ""
ssid = ""

for interface in os.listdir("/sys/class/net/"):
    if(interface.startswith("wlp") or interface.startswith("wlan")):
        stateFile = open("/sys/class/net/" + interface + "/operstate", "r")
        isUp = True if stateFile.read().strip() == "up" else False
        if(isUp):
            icon = "直"
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

                
        if("-n" in sys.argv):
            icon = ""
        
        if(isUp == "down"):
            print(icon)
        elif(isUp and hasIw):
            print(icon + str(quality) + "%", ssid)
        else:
            print(icon)
