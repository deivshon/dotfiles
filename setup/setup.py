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

# Check if the script is being run as root
currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

# Check dotfiles folder location
setupDir = os.path.dirname(os.path.realpath(__file__))

if(setupDir != os.path.expanduser("~/dotfiles/setup")):
    sys.exit("The dotfiles folder needs to be placed in your home folder!")

# Import printingUtils (../../scripts/scriptingUtils/printingUtils.py)
sys.path.insert(1, setupDir + "/../scripts/scriptingUtils/")

import printingUtils

subprocess.run([os.path.expanduser("~/dotfiles/setup/installs.sh"), "-d"])

f = open("links.json")
linksList = json.loads(f.read())
f.close()

forceLinks = False
if("-f" in sys.argv):
    forceLinks = True

for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    setupFlags = linksList[link]["setupFlags"]
    action = "Linking"

    # Creates the directory where the target file needs to be in
    makeDirs(linkTarget)

    linkFlags = "-sf" if forceLinks else "-si"
    command = ["ln", linkFlags, linkSource, linkTarget]

    if("copy" in setupFlags):
        command = ["cp", linkSource, linkTarget]
        action = "Copying"

    printingUtils.printCol(action + " ", "white", linkSource, "yellow", " to ", "white", linkTarget, "cyan")
    if("needsSudo" in setupFlags):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)

subprocess.run([os.path.expanduser("~/dotfiles/setup/installs.sh"), "-c"])
