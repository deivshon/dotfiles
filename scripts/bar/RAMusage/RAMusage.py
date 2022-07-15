#!/bin/python3

import sys
import os

label = "RAM "
suffix = "|" if "--separator" in sys.argv else ""

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.insert(1, scriptDir + "/../../scriptingUtils")

import scriptingUtils

memTotal = memAvailable = 0
meminfoOutput = scriptingUtils.pipeline([["cat", "/proc/meminfo"], ["grep", "-e", "MemTotal", "-e", "MemAvailable"]]).split("\n")[:2]
meminfoOutput = [int(scriptingUtils.whitelistChars(meminfoOutput[i], "0123456789")) for i in range(0, len(meminfoOutput))]
memTotal, memAvailable = meminfoOutput[0], meminfoOutput[1]

inUse = (memTotal - memAvailable)
percentageInUse = (inUse / memTotal) * 100
print(label + str(round(inUse / 1000000, 2)), "G/", str(round(memTotal / 1000000, 2)), "G (" + str(round(percentageInUse, 2)) + "%)" + suffix, sep="")
