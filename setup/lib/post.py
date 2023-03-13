import os
import stat
import subprocess

import setup.lib.printing as printing
import setup.lib.utils as utils

__DEFAULT_XINITRC = "/etc/X11/xinit/xinitrc"
__USER_XINITRC = os.path.expanduser("~/.xinitrc")
__STARTUP_SCRIPT = os.path.expanduser("~/startup/startup.sh")
__XINITRC_APPEND = "./.xinitrc_append"

# To be called only the first time the setup is run
def install():
	printing.colorPrint("Starting post install operations...", printing.MAGENTA)

	__xinitrc()
	printing.colorPrint(f"{__USER_XINITRC} handled", printing.WHITE)

	__startup_script()
	printing.colorPrint(f"{__STARTUP_SCRIPT} handled", printing.WHITE)

	__rustup()
	printing.colorPrint("Rustup handled", printing.WHITE)

	__reflector()
	printing.colorPrint("Reflector handled", printing.WHITE)

	printing.colorPrint("Ended post install operations...", printing.GREEN)

# To be called every time the setup is run
def change(colorStyle):
	printing.colorPrint("Starting post run operations...", printing.MAGENTA)

	__wallpaper(colorStyle)
	printing.colorPrint("Wallpaper handled", printing.WHITE)

	printing.colorPrint("Ended post run operations...", printing.GREEN)

def __wallpaper(colorStyle):
	user = os.path.expanduser("~")
	pictures = user + "/Pictures"

	# Download wallpaper and place it in ~/Pictures/wallpaper
	if not os.path.isdir(pictures):
		os.mkdir(pictures)

	wallpaperPath = user + "/Pictures/" + colorStyle["wallpaperName"]
	if not os.path.isfile(wallpaperPath):
		subprocess.run(["wget", colorStyle["wallpaperLink"], "-O", wallpaperPath])
	subprocess.run(["cp", wallpaperPath, user + "/Pictures/wallpaper"])

def __xinitrc():
	if os.path.isfile(__USER_XINITRC):
		printing.colorPrint(f"{__USER_XINITRC} already exists", printing.RED)
		return

	if not os.path.isfile(__DEFAULT_XINITRC):
		printing.colorPrint("Couldn't handle xinitrc: default xinitrc not found", printing.RED)
		return

	with open(__DEFAULT_XINITRC) as f:
		xinitrc = f.read().splitlines()

	if "twm &" not in xinitrc:
		printing.colorPrint("Couldn't handle xinitrc: malformed default xinitrc", printing.RED)
		return

	xinitrc = xinitrc[0:xinitrc.index("twm &")]

	with open(__XINITRC_APPEND, "r") as f:
		xinitrc_append = f.read()	

	with open(__USER_XINITRC, "w") as f:
		f.write("\n".join(xinitrc) + "\n" + xinitrc_append)

def __startup_script():
	# Create the startup folder and script in the home directory
	# This script is ran every time the X server starts
	utils.make_dirs(os.path.dirname(__STARTUP_SCRIPT))

	if not os.path.isfile(__STARTUP_SCRIPT):
		with open(__STARTUP_SCRIPT, "w") as f:
			f.write("#!/bin/sh\n")

		# This line is the equivalent of chmod +x ~/startup/startup.sh
		os.chmod(__STARTUP_SCRIPT, os.stat(__STARTUP_SCRIPT).st_mode | stat.S_IEXEC)
	else:
		printing.colorPrint(f"{__STARTUP_SCRIPT} already exists", printing.RED)

def __rustup():
	subprocess.run(["rustup", "default", "stable"])

def __reflector():
	subprocess.run(["sudo", "systemctl", "enable", "reflector.service"])
