#!/bin/python3

import os
import sys
import json
import argparse

from setup.lib import printing
from setup.lib import status
from setup.lib import install

__FILE_DIR__ = os.path.dirname(os.path.realpath(__file__))

DEFAULT_STYLE = f"{__FILE_DIR__}/../data/styles/sunsetDigital.json"

parser = argparse.ArgumentParser(
    prog="setup",
    description="Setup script for new installations or style changes"
)

parser.add_argument(
    "-f", "--force",
    action="store_true",
    help="Overwrite existing configuration targets without asking"
)
parser.add_argument(
    "-k", "--keep",
    action="store_true",
    help="Keep directory containing expanded configurations"
)
parser.add_argument(
    "-rm", "--remove",
    action="store_true",
    help="Remove existing configuration files"
)
parser.add_argument(
    "-p", "--packages",
    action="store_true",
    help="Force packages installation"
)
parser.add_argument(
    "-s", "--style",
    action="store",
    help="Path to file describing the style to apply (./setup/data/styles/[...])"
)

args = parser.parse_args()

# Check if the script is being run as root
if os.getuid() == 0:
    sys.exit("Don't run the script as root!")

currentUser = os.path.expanduser("~")
startDir = os.getcwd()
setupDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(setupDir)

if not os.path.isfile(status.SETUP_STATUS):
    setupStatus = status.new()
else:
    setupStatus = status.get()

installedInRun = False
if not setupStatus[status.PACKAGES_INSTALLED]:
    install.packages()
    setupStatus[status.PACKAGES_INSTALLED] = True
    installedInRun = True

# Imported here because they use modules that are only installed
# with install.packages
from setup.lib import configs
from setup.lib import style
from setup.lib import post
from setup.lib import utils

if args.remove:
    configs.remove(currentUser)
    quit()

if args.style is not None:
    # Style file path argument is relative to caller's cwd (startDir)
    os.chdir(startDir)
    args.style = os.path.abspath(os.path.expanduser(args.style))
    os.chdir(setupDir)
    printing.colorPrint(
        f"Selecting style from argument: ",
        printing.WHITE,
        utils.get_last_node(args.style),
        printing.MAGENTA
    )
else:
    if status.STYLE not in setupStatus:
        printing.colorPrint(
            f"Selecting default style: ",
            printing.WHITE,
            DEFAULT_STYLE,
            printing.MAGENTA
        )
        args.style = DEFAULT_STYLE
    else:
        printing.colorPrint(
            f"Selecting style from old setup data ({status.SETUP_STATUS}): ",
            printing.WHITE,
            utils.get_last_node(setupStatus[status.STYLE]),
            printing.MAGENTA
        )
        args.style = setupStatus[status.STYLE]

if not os.path.isfile(args.style):
    printing.colorPrint(
        f"{args.style} does not exist",
        printing.WHITE
    )
    quit()

# Package installation if it's been explicitly requested but not performed
# because the setup has been run before
if not installedInRun and args.packages:
    install.packages()
    setupStatus[status.PACKAGES_INSTALLED] = True

# Store style content
with open(args.style, "r") as f:
    selectedStyle = json.loads(f.read())

style.expand(selectedStyle)
style.check(selectedStyle)

install.download("dwm")
install.download("plstatus")
install.download("st")

configs.link(selectedStyle, currentUser,
             keepExpansions=args.keep, force=args.force)
setupStatus[status.STYLE] = os.path.abspath(args.style)

# Download and compile change-vol-pactl
install.install("change_vol_pactl")

install.compile("dwm")
install.compile("st")

post.change(selectedStyle)

if not setupStatus[status.POST_INSTALL_OPS]:
    post.install()
    setupStatus[status.POST_INSTALL_OPS] = True

# Install Rust programs after rust is configured,
# which happens only during the post install operations
install.status_scripts()
install.install("command_cache")

# Compile plstatus after status scripts are installed,
# otherwise commands in plstatus configuration will not exists in PATH
# at compile time and compilation will subsequently fail
install.compile("plstatus")

status.write(setupStatus)
