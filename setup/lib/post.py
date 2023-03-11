import os
import stat
import subprocess

import setup.lib.printing as printing

# To be called only the first time the setup is run
def install():
	printing.colorPrint("Running post install operations...", "green")

	__xinitrc()
	printing.colorPrint(".xinitrc handled", "white")

	__startup_script()
	printing.colorPrint("Startup script handled", "white")

# To be called every time the setup is run
def change():
	pass

def __xinitrc():
	if not os.path.isfile("/etc/X11/xinit/xinitrc"):
		printing.colorPrint("Couldn't handle xinitrc: default xinitrc not found", "red")
		return

	with open("/etc/X11/xinit/xinitrc") as f:
		xinitrc = f.read().splitlines()

	if "twm &" not in xinitrc:
		printing.colorPrint("Couldn't handle xinitrc: malformed default xinitrc", "red")
		return

	xinitrc = xinitrc[0:xinitrc.index("twm &")]

	with open(".xinitrc_append", "r") as f:
		xinitrc_append = f.read()
	
	xinitrcPath = os.path.expanduser("~/.xinitrc")
	if os.path.isfile(xinitrcPath):
		printing.colorPrint(f"{xinitrcPath} already exists", "red")

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
