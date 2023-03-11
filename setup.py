#!/bin/python3

import os
import sys
import subprocess
import json
import shutil

import setup.lib.install as install

DATA_FILE = "./setup/data/data.json"
FIRST_RUN_FILE = ".notFirstRun"
DEFAULT_COLOR_STYLE = "./setup/data/colorStyles/sunsetDigital.json"
EXPANSIONS_DIR = "./expansions/"

firstRun = not os.path.isfile(FIRST_RUN_FILE)

if firstRun:
    install.packages(FIRST_RUN_FILE)

import setup.lib.printing as printing
import setup.lib.expand as expand
import setup.lib.post as post


###########################################
#            INITIAL CHECKS               #
###########################################


# Check if the script is being run as root
currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

# Check dotfiles folder location
setupDir = os.path.dirname(os.path.realpath(__file__))

if(setupDir != os.path.expanduser("~/dotfiles")):
    sys.exit("The dotfiles folder needs to be placed in your home folder!")


###########################################
#            GENERIC UTILITIES            #
###########################################


# Assumes the path parameter starts with / and is a path to a file
def makeDirs(path):
    subprocess.run(["mkdir", "-p", path])

def getLastNode(path):
    return path[::-1][0:path[::-1].index("/")][::-1]

def checkColorStyle(colorStyle, neededFields):
    # Check the selected color style contains all the needed fields
    colorStyleKeys = colorStyle.keys()
    if "substitutions" not in colorStyleKeys:
        sys.exit("Substitutions field missing in color style")

    for field in neededFields["other"]:
        if field not in colorStyleKeys:
            sys.exit("Field missing in color style: " + field)

    colorStyleSubstitutionKeys = colorStyle["substitutions"].keys()

    for field in neededFields["substitutions"]:
        if field not in colorStyleSubstitutionKeys:
            sys.exit("Sub-field missing in substitutions field: " + field)
    
    for field in neededFields["setup-expanded-substitutions"]:
        if field not in colorStyleSubstitutionKeys:
            sys.exit("Sub-field missing in substitutions field: " + field + "\nThis is an automatically generated field, so something has gone wrong during the setup")


###########################################
#        SETUP SPECIFIC FUNCTIONS         #
###########################################


def removeConfigs(linksList):
    for link in linksList:
        linkTarget = linksList[link]["target"].replace("~", currentUser)
        needsSudo = "needsSudo" in linksList[link]["setupFlags"]

        removeCommand = ["rm", linkTarget]
        if(needsSudo): removeCommand.insert(0, "sudo")
        if(os.path.isfile(linkTarget)):
            printing.colorPrint("Removing ", "white", linkTarget, "red")
            subprocess.run(removeCommand)
        else:
            printing.colorPrint("Can't find ", "white", linkTarget, "red")


###########################################
#                  MAIN                   #
###########################################


# Store necessary data
with open(DATA_FILE, "r") as f:
    data = json.loads(f.read())

linksList = data["links"]
neededFields = data["neededFields"]

# Arguments handling
colorStylePath = DEFAULT_COLOR_STYLE
forceLinks = False
keepExpansionsDir = False
forcePackageInstall = False
for i in range(0, len(sys.argv)):
    if(sys.argv[i] == "-f"):    # -f -> force
        forceLinks = True
    elif(sys.argv[i] == "-k"):  # -k -> keep
        keepExpansionsDir = True
    elif(sys.argv[i] == "-rm"): # -rm -> remove configs
        removeConfigs(linksList)
        quit()
    elif(sys.argv[i] == "-p"):  # -p -> packages
        forcePackageInstall = True
    elif(sys.argv[i] == "-s"):  # -s -> style (color style path)
        if(i + 1 >= len(sys.argv)):
            # No color style path provided after -s flag, quit
            print("Provide a path to the color style file")
            quit()
        if(not os.path.isfile(sys.argv[i + 1])):
            print("Path to color style file is not valid")
            quit()
        # Color style argument checks done, path can be saved safely
        colorStylePath = sys.argv[i + 1]

# Package installation if it's been explicitly requested but not performed
# because the setup has been run before
if not firstRun and forcePackageInstall:
    install.packages(FIRST_RUN_FILE)

# Read and store color style content
with open(colorStylePath, "r") as f:
    colorStyle = json.loads(f.read())

expand.expandColorStyle(colorStyle, data)
checkColorStyle(colorStyle, neededFields)

# Download the dwm, plstatus, st builds and status-scripts
install.download("dwm")
install.download("plstatus")
install.download("st")
install.download("status_scripts")

# Handle each link/copy
for link in linksList:
    linkSource = linksList[link]["source"].replace("$(setupDir)", setupDir)
    linkTarget = linksList[link]["target"].replace("~", currentUser)
    setupFlags = linksList[link]["setupFlags"]
    action = "Linking"

    # Create the directory where the target file needs to be in
    makeDirs(os.path.dirname(linkTarget))

    linkFlags = "-sf" if forceLinks else "-si"
    command = ["ln", linkFlags, linkSource, linkTarget]

    if("needsSubstitution" in setupFlags):
        if("copy" not in setupFlags): setupFlags.append("copy")

        # If the temporary directory has not yet been created, create it
        if(not os.path.isdir(EXPANSIONS_DIR)):
            os.mkdir(EXPANSIONS_DIR)

        subprocess.run(["cp", linkSource, EXPANSIONS_DIR])
        linkSource = EXPANSIONS_DIR + getLastNode(linkSource)

        # Perform the necessary substitutions using sed
        substitutions = colorStyle["substitutions"]
        for identifier in substitutions:
            subprocess.run(["sed", "-i", "s/" + identifier + "/" + substitutions[identifier] + "/g", linkSource])

    if("copy" in setupFlags):
        command = ["cp", linkSource, linkTarget]
        action = "Copying"

    printing.colorPrint(action + " ", "white", linkSource, "yellow", " to ", "white", linkTarget, "cyan")
    if("needsSudo" in setupFlags):
        subprocess.run(["sudo"] + command)
    else:
        subprocess.run(command)

# Delete temporary directory unless the user specified not to
if(not keepExpansionsDir and os.path.isdir(EXPANSIONS_DIR)):
    shutil.rmtree(EXPANSIONS_DIR)

# Download and compile change-vol-pactl
install.install("change_vol_pactl")

# Compile dwm, plstatus, st and status-scripts
install.compile("dwm")
install.compile("plstatus")
install.compile("st")
install.compile("status_scripts")

# Download wallpaper and place it in ~/Pictures/wallpaper
if(not os.path.isdir(os.path.expanduser("~/Pictures"))):
    os.mkdir(os.path.expanduser("~/Pictures/"))

wallpaperPath = currentUser + "/Pictures/" + colorStyle["wallpaperName"]
if(not os.path.isfile(wallpaperPath)):
    subprocess.run(["wget", colorStyle["wallpaperLink"], "-O", wallpaperPath])
subprocess.run(["cp", wallpaperPath, currentUser + "/Pictures/wallpaper"])

if firstRun:
    post.install()
