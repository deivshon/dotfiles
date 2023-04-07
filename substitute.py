#!/bin/python3

import os
import sys
import json
import argparse
from time import time

try:
    import setup.lib.configs as configs
    import setup.lib.style as style
    import setup.lib.utils as utils
except Exception as e:
    print(f"An error occurred while importing needed modules: {e}\nEnsure matplotlib is installed")
    sys.exit(1)

parser = argparse.ArgumentParser(
    prog = "substitute",
    description = "Perform configs substitutions for a specified color style"
)

parser.add_argument(
    "-s", "--style",
    action = "store",
    help = "Path to file describing the style to apply (./setup/data/styles/[...])",
	required = True
)

parser.add_argument(
    "-o", "--output-dir",
    action = "store",
    help = "Output directory",
	required = False
)

args = parser.parse_args()

# Store style content
with open(args.style, "r") as f:
    selectedStyle = json.loads(f.read())

style.expand(selectedStyle)
style.check(selectedStyle)

if args.output_dir is None:
    styleName = utils.get_last_node(args.style)
    substitutionsDir = f"{configs.SUBSTITUTIONS_DIR}_{styleName}_{time():.0f}"

    # Ensure subsitutions directory does not exist already
    i = 2
    while os.path.exists(substitutionsDir):
        substitutionsDir = f"{configs.SUBSTITUTIONS_DIR}_{styleName}_{time():.0f}_{i}"
        i += 1
else:
    substitutionsDir = args.output_dir

configs.substitute(selectedStyle, substitutionsDir)
