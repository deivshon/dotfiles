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

for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    needSudo = linksList[link]["needSudo"]

    command = ["ln", "-si", linkSource, linkTarget]

    print("Linking", linkSource, "to", linkTarget)
    if(needSudo):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)
