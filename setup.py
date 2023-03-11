#!/bin/python3

import os
import sys
import subprocess
import json
import shutil

import setup.lib.install as install

FIRST_RUN_FILE = ".notFirstRun"
DEFAULT_STYLE = "./setup/data/styles/sunsetDigital.json"

firstRun = not os.path.isfile(FIRST_RUN_FILE)

if firstRun:
    install.packages(FIRST_RUN_FILE)

import setup.lib.configs as configs
import setup.lib.style as style
import setup.lib.post as post

# Check if the script is being run as root
currentUser = os.path.expanduser("~")
if(currentUser == "/root"):
    sys.exit("Don't run the script as root!")

# Check dotfiles folder location
setupDir = os.path.dirname(os.path.realpath(__file__))

if(setupDir != os.path.expanduser("~/dotfiles")):
    sys.exit("The dotfiles folder needs to be placed in your home folder!")

# Arguments handling
colorStylePath = DEFAULT_STYLE
force = False
keepExpansions = False
forcePackageInstall = False
for i in range(0, len(sys.argv)):
    if(sys.argv[i] == "-f"):    # -f -> force
        force = True
    elif(sys.argv[i] == "-k"):  # -k -> keep
        keepExpansions = True
    elif(sys.argv[i] == "-rm"): # -rm -> remove configs
        configs.remove(currentUser)
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
    selectedStyle = json.loads(f.read())

style.expand(selectedStyle)
style.check(selectedStyle)

# Download the dwm, plstatus, st builds and status-scripts
install.download("dwm")
install.download("plstatus")
install.download("st")
install.download("status_scripts")

configs.link(selectedStyle, currentUser, setupDir, keepExpansions = keepExpansions, force = force)

# Download and compile change-vol-pactl
install.install("change_vol_pactl")

# Compile dwm, plstatus, st and status-scripts
install.compile("dwm")
install.compile("plstatus")
install.compile("st")
install.compile("status_scripts")

post.change(selectedStyle)

if firstRun:
    post.install()
