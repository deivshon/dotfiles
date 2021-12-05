#!/bin/python3

import os
import sys
import subprocess
import json

setupDir = os.path.dirname(os.path.realpath(__file__))

f = open("links.json")
linksList = json.loads(f.read())
f.close()

currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

forceLinks = False
if(len(sys.argv) > 1 and sys.argv[1] == "-f"):
    forceLinks = True

for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    needSudo = linksList[link]["needSudo"]

    flags = "-sf" if forceLinks else "-si"
    command = ["ln", flags, linkSource, linkTarget]

    print("Linking", linkSource, "to", linkTarget)
    if(needSudo):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)
