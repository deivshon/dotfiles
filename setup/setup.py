#!/bin/python3

import os
import sys
import subprocess
import json
import shutil

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

def getLastNode(path):
    return path[::-1][0:path[::-1].index("/")][::-1]

def removeConfigs(linksList):
    for link in linksList:
        linkTarget = linksList[link]["target"].replace("~", currentUser)
        needsSudo = "needsSudo" in linksList[link]["setupFlags"]

        removeCommand = ["rm", linkTarget]
        if(needsSudo): removeCommand.insert(0, "sudo")
        if(os.path.isfile(linkTarget)):
            printingUtils.printCol("Removing ", "white", linkTarget, "red")
            subprocess.run(removeCommand)
        else:
            printingUtils.printCol("Can't find ", "white", linkTarget, "red")

# Read and store link/copy data from links.json
with open("links.json", "r") as f:
    linksList = json.loads(f.read())

# Arguments handling
colorPackagePath = "defaultColorPackage.json"
forceLinks = False
keepColorsTmpDir = False
for i in range(0, len(sys.argv)):
    if(sys.argv[i] == "-f"):    # -f -> force
        forceLinks = True
    elif(sys.argv[i] == "-k"):  # -k -> keep
        keepColorsTmpDir = True
    elif(sys.argv[i] == "-rm"): # -rm -> remove configs
        removeConfigs(linksList)
        quit()
    elif(sys.argv[i] == "-s"):  # -s -> style (color package path)
        if(i + 1 >= len(sys.argv)):
            # No color package path provided after -s flag, quit
            print("Provide a path to the color package file")
            quit()
        if(not os.path.isfile(sys.argv[i + 1])):
            print("Path to color package file is not valid")
            quit()
        # Color package argument checks done, path can be saved safely
        colorPackagePath = sys.argv[i + 1]

# Read and store color package content
with open(colorPackagePath, "r") as f:
    colorPackage = json.loads(f.read())

# Download the dwm and slstatus builds using the installs.sh script
subprocess.run([os.path.expanduser("~/dotfiles/setup/installs.sh"), "-d"])

# Handle each link/copy
for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    setupFlags = linksList[link]["setupFlags"]
    action = "Linking"

    # Create the directory where the target file needs to be in
    makeDirs(linkTarget)

    linkFlags = "-sf" if forceLinks else "-si"
    command = ["ln", linkFlags, linkSource, linkTarget]

    if("needsSubstitution" in setupFlags):
        if("copy" not in setupFlags): setupFlags.append("copy")

        # If the temporary directory has not yet been created, create it
        if(not os.path.isdir("../colorsTmp/")):
            os.mkdir("../colorsTmp/")

        subprocess.run(["cp", linkSource, "../colorsTmp/"])
        linkSource = "../colorsTmp/" + getLastNode(linkSource)

        # Perform the necessary substitutions using sed
        subprocess.run(["sed", "-i", "s/mainColor/" + colorPackage["mainColor"] + "/g", linkSource])
        subprocess.run(["sed", "-i", "s/secondaryColor/" + colorPackage["secondaryColor"] + "/g", linkSource])

    if("copy" in setupFlags):
        command = ["cp", linkSource, linkTarget]
        action = "Copying"

    printingUtils.printCol(action + " ", "white", linkSource, "yellow", " to ", "white", linkTarget, "cyan")
    if("needsSudo" in setupFlags):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)

# Delete temporary directory unless the user specified not to
if(not keepColorsTmpDir and os.path.isdir("../colorsTmp/")):
    shutil.rmtree("../colorsTmp/")

# Download wallpaper and place it in ~/Pictures/wallpaper
if(not os.path.isdir(os.path.expanduser("~/Pictures"))):
    os.mkdir(os.path.expanduser("~/Pictures/"))

wallpaperPath = currentUser + "/Pictures/" + colorPackage["wallpaperName"]
if(not os.path.isfile(wallpaperPath)):
    subprocess.run(["wget", colorPackage["wallpaperLink"], "-O", wallpaperPath])
subprocess.run(["cp", wallpaperPath, currentUser + "/Pictures/wallpaper"])

# Compile dwm and slstatus using the installs.sh script
subprocess.run([os.path.expanduser("~/dotfiles/setup/installs.sh"), "-c"])
