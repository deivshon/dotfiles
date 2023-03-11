import os
import stat
import subprocess

import setup.lib.printing as printing

# To be called only the first time the setup is run
def install():
	printing.colorPrint("Starting post install operations...", printing.MAGENTA)

	__xinitrc()
	printing.colorPrint(".xinitrc handled", printing.WHITE)

	__startup_script()
	printing.colorPrint("Startup script handled", printing.WHITE)

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
	if(not os.path.isfile(wallpaperPath)):
		subprocess.run(["wget", colorStyle["wallpaperLink"], "-O", wallpaperPath])
	subprocess.run(["cp", wallpaperPath, user + "/Pictures/wallpaper"])

def __xinitrc():
	if not os.path.isfile("/etc/X11/xinit/xinitrc"):
		printing.colorPrint("Couldn't handle xinitrc: default xinitrc not found", printing.RED)
		return

	with open("/etc/X11/xinit/xinitrc") as f:
		xinitrc = f.read().splitlines()

	if "twm &" not in xinitrc:
		printing.colorPrint("Couldn't handle xinitrc: malformed default xinitrc", printing.RED)
		return

	xinitrc = xinitrc[0:xinitrc.index("twm &")]

	with open(".xinitrc_append", "r") as f:
		xinitrc_append = f.read()
	
	xinitrcPath = os.path.expanduser("~/.xinitrc")
	if os.path.isfile(xinitrcPath):
		printing.colorPrint(f"{xinitrcPath} already exists", printing.RED)

	with open(xinitrcPath, "w") as f:
		f.write("\n".join(xinitrc) + "\n" + xinitrc_append)

def __startup_script():
	# Create the startup folder and script in the home directory
	# This script is ran every time the X server starts
	subprocess.run(["mkdir", "-p", os.path.expanduser("~/startup")])

	startupFilePath = os.path.expanduser("~/startup/startup.sh")
	if not os.path.isfile(startupFilePath):
		with open(startupFilePath, "w") as f:
			f.write("#!/bin/sh\n")

		# This line is the equivalent of chmod +x ~/startup/startup.sh
		os.chmod(startupFilePath, os.stat(startupFilePath).st_mode | stat.S_IEXEC)
