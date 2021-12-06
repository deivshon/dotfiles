#!/bin/python3

import os
import sys
import subprocess
import json

# Assumes the path parameter starts with / and is a path to a file
def makeDirs(pathToFile):
    dirNames = pathToFile.split("/")
    dirNames = [dirNames[i] for i in range(0, len(dirNames)) if dirNames[i] != ""]
    
    # Loop skips first and last element as the first is empty and the last is the file name
    # At the end of the loop, the directory where to put the file exists
    for i in range(1, len(dirNames)):
        dir = "/" + "/".join(dirNames[0:i])
        if(not os.path.isdir(dir)):
            print("Directory", dir, "doesn't exist, creating it")
            os.mkdir(dir)

currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

setupDir = os.path.dirname(os.path.realpath(__file__))

if(setupDir != os.path.expanduser("~/dotfiles/setup")):
    sys.exit("The dotfiles folder needs to be placed in your home folder!")

f = open("links.json")
linksList = json.loads(f.read())
f.close()

forceLinks = False
if(len(sys.argv) > 1 and sys.argv[1] == "-f"):
    forceLinks = True

for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    needSudo = linksList[link]["needSudo"]

    # Creates the directory where the target file needs to be in
    makeDirs(linkTarget)

    flags = "-sf" if forceLinks else "-si"
    command = ["ln", flags, linkSource, linkTarget]

    print("Linking", linkSource, "to", linkTarget)
    if(needSudo):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)
