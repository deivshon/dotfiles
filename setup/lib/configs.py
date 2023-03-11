import os
import subprocess
import json
import shutil

import setup.lib.printing as printing
import setup.lib.utils as utils

__EXPANSIONS_DIR = "./expansions/"
__LINKS_FILE = "./setup/data/links.json"

with open(__LINKS_FILE, "r") as f:
    __linksList = json.loads(f.read())

def link(style, user, setupDir, keepExpansions = False, force = False):
	linkFlags = "-sf" if force else "-si"

	# Handle each link/copy
	for link in __linksList:
		linkSource = __linksList[link]["source"].replace("$(setupDir)", setupDir)
		linkTarget = __linksList[link]["target"].replace("~", user)
		setupFlags = __linksList[link]["setupFlags"]
		action = "Linking"

		# Create the directory where the target file needs to be in
		utils.make_dirs(os.path.dirname(linkTarget))

		command = ["ln", linkFlags, linkSource, linkTarget]

		if("needsSubstitution" in setupFlags):
			if("copy" not in setupFlags): setupFlags.append("copy")

	        # If the temporary directory has not yet been created, create it
			if(not os.path.isdir(__EXPANSIONS_DIR)):
				os.mkdir(__EXPANSIONS_DIR)

			subprocess.run(["cp", linkSource, __EXPANSIONS_DIR])
			linkSource = __EXPANSIONS_DIR + utils.get_last_node(linkSource)

	        # Perform the necessary substitutions using sed
			substitutions = style["substitutions"]
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
	if(not keepExpansions and os.path.isdir(__EXPANSIONS_DIR)):
		shutil.rmtree(__EXPANSIONS_DIR)

def remove(user):
    for link in __linksList:
        linkTarget = __linksList[link]["target"].replace("~", user)
        needsSudo = "needsSudo" in __linksList[link]["setupFlags"]

        removeCommand = ["rm", linkTarget]
        if(needsSudo): removeCommand.insert(0, "sudo")
        if(os.path.isfile(linkTarget)):
            printing.colorPrint("Removing ", "white", linkTarget, "red")
            subprocess.run(removeCommand)
        else:
            printing.colorPrint("Can't find ", "white", linkTarget, "red")
