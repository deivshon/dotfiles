#!/bin/python3

import os
import sys
import json
import argparse

import setup.lib.install as install

FIRST_RUN_FILE = ".notFirstRun"
DEFAULT_STYLE = "./setup/data/styles/sunsetDigital.json"

parser = argparse.ArgumentParser(
    prog = "setup",
    description = "Setup script for new installations or style changes"
)

parser.add_argument(
    "-f", "--force",
    action = "store_true",
    help = "Overwrite existing configuration targets without asking"
)
parser.add_argument(
    "-k", "--keep",
    action = "store_true",
    help = "Keep directory containing expanded configurations"
)
parser.add_argument(
    "-rm", "--remove",
    action = "store_true",
    help = "Remove existing configuration files"
)
parser.add_argument(
    "-p", "--packages",
    action = "store_true",
    help = "Force packages installation"
)
parser.add_argument(
    "-s", "--style",
    action = "store",
    help = "Path to file describing the style to apply (./setup/data/styles/[...])",
    default = DEFAULT_STYLE
)

args = parser.parse_args()

# Check if the script is being run as root
if os.getuid() == 0:
    sys.exit("Don't run the script as root!")

currentUser = os.path.expanduser("~")
startDir = os.getcwd()
setupDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(setupDir)

firstRun = not os.path.isfile(FIRST_RUN_FILE)

if firstRun:
    install.packages(FIRST_RUN_FILE)

# Imported here because they use modules that are only installed
# with install.packages
import setup.lib.configs as configs
import setup.lib.style as style
import setup.lib.post as post

if args.remove:
    configs.remove(currentUser)
    quit()

# Style file path is relative to caller's cwd (startDir)
if args.style != None:
    os.chdir(startDir)
    args.style = os.path.abspath(os.path.expanduser(args.style))
    os.chdir(setupDir)

if not os.path.isfile(args.style):
    print(f"{args.style} does not exist")
    quit()

# Package installation if it's been explicitly requested but not performed
# because the setup has been run before
if not firstRun and args.packages:
    install.packages(FIRST_RUN_FILE)

# Store style content
with open(args.style, "r") as f:
    selectedStyle = json.loads(f.read())

style.expand(selectedStyle)
style.check(selectedStyle)

install.download("dwm")
install.download("plstatus")
install.download("st")
install.download("status_scripts")

configs.link(selectedStyle, currentUser, setupDir, keepExpansions = args.keep, force = args.force)

# Download and compile change-vol-pactl
install.install("change_vol_pactl")

install.compile("dwm")
install.compile("st")

post.change(selectedStyle)

if firstRun:
    post.install()

# Compile status scripts after rust is configured,
# which happens only during the post install operations
install.compile("status_scripts")

# Compile plstatus after status scripts are installed,
# otherwise commands in plstatus configuration will not exists in PATH
# at compile time and compilation will subsequently fail
install.compile("plstatus")
