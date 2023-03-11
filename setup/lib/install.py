import sys
import subprocess
import os
import json
from time import time as currentTimestamp

__PACMAN = "pacman"
__YAY = "yay"
__acceptedInstallPrograms = [
	"yay",
	"dwm",
	"plstatus",
	"change_vol_pactl",
	"st",
	"status_scripts",
]

def __script(program, action):
	if program not in __acceptedInstallPrograms:
		sys.exit(f"Program {program} can't be installed")

	subprocess.run(["./setup/lib/installs.sh", program, action])

def install(program):
	__script(program, "i")

def download(program):
	__script(program, "d")

def compile(program):
	__script(program, "c")

def packages(firstRunDetectionFile):
	with open("./setup/data/packages.json") as f:
		packages = json.loads(f.read())

	if not os.path.isdir(os.path.expanduser("~/yay")):
		install("yay")

	pacmanCommand = \
		["sudo", "pacman", "-Syu"] + \
		packages[__PACMAN] + \
		["--needed"]

	yayCommand = \
		["yay", "-Sua"] + \
		packages[__YAY] + \
		["--needed"]

	subprocess.run(pacmanCommand)
	subprocess.run(yayCommand)

	# Create a file containing the current timestamp to mark that the script
	# has been run at least once in the past and the packages have been installed
	with open(firstRunDetectionFile, "w") as f:
		f.write(str(currentTimestamp()) + "\n")
