import os
import subprocess
import json
import shutil

import setup.lib.printing as printing
import setup.lib.utils as utils

__EXPANSIONS_DIR = "./expansions/"
__LINKS_FILE = "./setup/data/links.json"

__SOURCE = "source"
__TARGET = "target"
__FLAGS = "flags"
__COPY_FLAG = "copy"
__SUBS = "subs"
__STYLE_SUBS = "substitutions"
__SUDO_FLAG = "sudo"

with open(__LINKS_FILE, "r") as f:
    __linksList = json.loads(f.read())

def link(style, user, setupDir, keepExpansions = False, force = False):
	linkFlags = "-sf" if force else "-si"

	# Handle each link/copy
	for link in __linksList:
		linkSource = __linksList[link][__SOURCE].replace("$(setupDir)", setupDir)
		linkTarget = __linksList[link][__TARGET].replace("~", user)
		setupFlags = __linksList[link][__FLAGS] if __FLAGS in __linksList[link] else []
		action = "Linking"

		# Create the directory where the target file needs to be in
		utils.make_dirs(os.path.dirname(linkTarget))

		command = ["ln", linkFlags, linkSource, linkTarget]

		substitutionIds = []
		if __SUBS in __linksList[link]:
			substitutionIds = __linksList[link][__SUBS]

		if len(substitutionIds) > 0:
			if __COPY_FLAG not in setupFlags:
				setupFlags.append(__COPY_FLAG)

	        # If the temporary directory has not yet been created, create it
			if not os.path.isdir(__EXPANSIONS_DIR):
				os.mkdir(__EXPANSIONS_DIR)

			subprocess.run(["cp", linkSource, __EXPANSIONS_DIR])
			linkSource = os.path.abspath(__EXPANSIONS_DIR + utils.get_last_node(linkSource))

	        # Perform the necessary substitutions using sed
			substitutionVals = style[__STYLE_SUBS]
			for id in substitutionIds:
				subprocess.run(["sed", "-i", "s/" + substitutionIds[id] + "/" + substitutionVals[id] + "/g", linkSource])

		if __COPY_FLAG in setupFlags:
			command = ["cp", linkSource, linkTarget]
			action = "Copying"

		printing.colorPrint(
			action + " ", 	printing.WHITE,
			linkSource, 	printing.YELLOW,
			" to ", 		printing.WHITE,
			linkTarget,		printing.CYAN
		)

		if __SUDO_FLAG in setupFlags:
			subprocess.run(["sudo"] + command)
		else:
			subprocess.run(command)

	# Delete temporary directory unless the user specified not to
	if not keepExpansions and os.path.isdir(__EXPANSIONS_DIR):
		shutil.rmtree(__EXPANSIONS_DIR)

def remove(user):
    for link in __linksList:
        linkTarget = __linksList[link][__TARGET].replace("~", user)
        needsSudo = __SUDO_FLAG in __linksList[link][__FLAGS]

        removeCommand = ["rm", linkTarget]
        if needsSudo: removeCommand.insert(0, "sudo")
        if os.path.isfile(linkTarget):
            printing.colorPrint(
				"Removing ",	printing.WHITE,
				linkTarget,		printing.RED
			)
            subprocess.run(removeCommand)
        else:
            printing.colorPrint(
				"Can't find ",	printing.WHITE,
				linkTarget,		printing.RED
			)
