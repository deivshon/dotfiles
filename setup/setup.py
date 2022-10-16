#!/bin/python3

import os
import sys
import stat
import subprocess
import json
import shutil
from time import time as currentTimestamp


###########################################
#            INITIAL CHECKS               #
###########################################


# Check if the script is being run as root
currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

# Check dotfiles folder location
setupDir = os.path.dirname(os.path.realpath(__file__))

if(setupDir != os.path.expanduser("~/dotfiles/setup")):
    sys.exit("The dotfiles folder needs to be placed in your home folder!")


###########################################
#            GENERIC UTILITIES            #
###########################################


def dirFromFile(pathToFile):
    splitPath = pathToFile.split("/")
    while(splitPath[len(splitPath) - 1] == ""):
        splitPath.pop()

    splitPath.pop()
    return "/".join(splitPath)

# Assumes the path parameter starts with / and is a path to a file
def makeDirs(pathToFile):
    subprocess.run(["mkdir", "-p", dirFromFile(pathToFile)])

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


def installs(program, action):
    subprocess.run([os.path.expanduser("~/dotfiles/setup/installs.sh"), program, action])

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

def installYay():
    if(not os.path.isdir(os.path.expanduser("~/yay"))):
        installs("yay", "i")

def installPackages(packages, firstRunDetectionFile):
    pacmanPackages = packages["pacman"]
    yayPackages = packages["yay"]

    pacmanPackages.insert(0, "-Syu")
    pacmanPackages.insert(0, "pacman")
    pacmanPackages.insert(0, "sudo")
    pacmanPackages.append("--needed")

    yayPackages.insert(0, "-Sua")
    yayPackages.insert(0, "yay")
    yayPackages.append("--needed")

    subprocess.run(pacmanPackages)
    subprocess.run(yayPackages)

    # Create a file containing the current timestamp to mark that the script
    # has been run at least once in the past. In the case of successive setup
    # runs, the script will not try to install all the packages (unless
    # otherwise specified with the -p flag), since they are likey to be
    # already installed
    with open(firstRunDetectionFile, "w") as f:
        f.write(str(currentTimestamp()) + "\n")

def handleXinitrc():
    if(not os.path.isfile("/etc/X11/xinit/xinitrc")):
        printingUtils.printCol("Couldn't handle xinitrc: default xinitrc not found", "red")
        return

    with open("/etc/X11/xinit/xinitrc") as f:
        xinitrc = f.read().splitlines()

    if("twm &" not in xinitrc):
        printingUtils.printCol("Couldn't handle xinitrc: malformed default xinitrc", "red")
        return

    xinitrc = xinitrc[0:xinitrc.index("twm &")]

    with open("../.xinitrc_append", "r") as f:
        xinitrc_append = f.read()

    with open(os.path.expanduser("~/.xinitrc"), "w") as f:
        f.write("\n".join(xinitrc) + "\n" + xinitrc_append)


###########################################
#      EXPANSION SPECIFIC FUNCTIONS       #
###########################################


def expandColorStyle(colorStyle, data):
    expand_efy(colorStyle, data)

def expand_efy(colorStyle, data):
    mainColor = colorStyle["substitutions"]["mainColor"]
    
    efyFields = data["expansion-data"]["enhancer-for-youtube"]
    newFields = {}

    for col in efyFields.keys():
        _, s, v = scriptingUtils.hex_to_divided_hsv(efyFields[col])
        newFields[col] = scriptingUtils.apply_hue(s, v, mainColor)    

    for field in newFields:
        if(field not in colorStyle["substitutions"]):
            colorStyle["substitutions"][field] = newFields[field]


###########################################
#                  MAIN                   #
###########################################


# Store necessary data
with open("data.json", "r") as f:
    data = json.loads(f.read())

linksList = data["links"]
packages = data["packages"]
neededFields = data["neededFields"]

# Arguments handling
colorStylePath = "./colorStyles/sunsetDigital.json"
forceLinks = False
keepColorsTmpDir = False
forcePackageInstall = False
for i in range(0, len(sys.argv)):
    if(sys.argv[i] == "-f"):    # -f -> force
        forceLinks = True
    elif(sys.argv[i] == "-k"):  # -k -> keep
        keepColorsTmpDir = True
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

# Package installation if it's the first time the script is ran
firstRunDetectionFile = "../.notFirstRun"

if(not os.path.isfile(firstRunDetectionFile) or forcePackageInstall):
    installYay()
    installPackages(packages, firstRunDetectionFile)

# Import utils (../../scripts/scriptingUtils/[...]utils.py)
# Placed here because the utils files import libraries that need
# to be installed with installPackages
sys.path.insert(1, setupDir + "/../scripts/scriptingUtils/")
import printingUtils
import scriptingUtils

# Read and store color style content
with open(colorStylePath, "r") as f:
    colorStyle = json.loads(f.read())

expandColorStyle(colorStyle, data)
checkColorStyle(colorStyle, neededFields)

# Download the dwm, slstatus and st builds using the installs.sh script
installs("dwm", "d")
installs("slstatus", "d")
installs("st", "d")

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
        substitutions = colorStyle["substitutions"]
        for identifier in substitutions:
            subprocess.run(["sed", "-i", "s/" + identifier + "/" + substitutions[identifier] + "/g", linkSource])

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

wallpaperPath = currentUser + "/Pictures/" + colorStyle["wallpaperName"]
if(not os.path.isfile(wallpaperPath)):
    subprocess.run(["wget", colorStyle["wallpaperLink"], "-O", wallpaperPath])
subprocess.run(["cp", wallpaperPath, currentUser + "/Pictures/wallpaper"])

# Compile dwm, slstatus and st using the installs.sh script
installs("dwm", "c")
installs("slstatus", "c")
installs("st", "c")

# Download and compile change-vol-pactl
installs("change_vol_pactl", "i")

# Compile C bar scripts
subprocess.run(["make", "clean", "all", "-C", os.path.expanduser("~/dotfiles/scripts/bar"), "dbg=false"])

# Use the default xinitrc file to create the final one using .xinitrc_append
if(not os.path.isfile(os.path.expanduser("~/.xinitrc"))):
    handleXinitrc()

# Create the setup folder and script in the home directory
# This script is ran every time the X server starts
subprocess.run(["mkdir", "-p", os.path.expanduser("~/startup")])

startupFilePath = os.path.expanduser("~/startup/startup.sh")
if(not os.path.isfile(startupFilePath)):
    with open(startupFilePath, "w") as f:
        f.write("#!/bin/sh\n")

    # This line is the equivalent of chmod +x ~/startup/startup.sh
    os.chmod(startupFilePath, os.stat(startupFilePath).st_mode | stat.S_IEXEC)
