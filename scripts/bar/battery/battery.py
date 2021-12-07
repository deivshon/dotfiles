#!/bin/python3

import os
import sys
import subprocess

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.insert(1, scriptDir + "/../../scriptingUtils")

import scriptingUtils

acpiProc = subprocess.run(["acpi", "-b"], capture_output = True)
acpiOut = acpiProc.stdout.decode().strip()

if("unavailable" in acpiOut):
    print("NO BAT")
else:
    acpiOut = acpiOut.split(",")

    charging = ""
    charge = ""
    remaining = ""

    for section in acpiOut:
        if("Charging" in section):
            charging = "CHR "
        if("%" in section):
            charge = scriptingUtils.whitelistChars(section, "0123456789%")
        if("remaining" in section):
            remaining = scriptingUtils.whitelistChars(section, "0123456789:")

print(charging, charge, " ", remaining, sep = "")
