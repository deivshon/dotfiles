#!/bin/python3

import os
import sys
import subprocess

label = "BAT "

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.insert(1, scriptDir + "/../../scriptingUtils")

import scriptingUtils

acpiProc = subprocess.run(["acpi", "-b"], capture_output = True)
acpiOut = (acpiProc.stdout.decode() + acpiProc.stderr.decode()).strip().lower()

if("unavailable" in acpiOut or "no support" in acpiOut or acpiOut == ""):
    quit()
else:
    acpiOut = acpiOut.split(",")

    charging = ""
    charge = ""
    remaining = ""

    for section in acpiOut:
        if(not "discharging" in section and "charging" in section):
            charging = "CHR "
        if("%" in section):
            charge = scriptingUtils.whitelistChars(section, "0123456789%")
        if("remaining" in section or "until" in section):
            remaining = " " + scriptingUtils.whitelistChars(section, "0123456789:")[:5]
    print(label + charging, charge, remaining, "|", sep = "")
