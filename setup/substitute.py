import os
import json
import argparse

from time import time
from setup.lib import utils
from setup.lib.style import style
from setup.lib.configs import configs


def main():
    parser = argparse.ArgumentParser(
        prog="substitute",
        description="Perform configs substitutions for a specified color style"
    )

    parser.add_argument(
        "-s", "--style",
        action="store",
        help="Path to file describing the style to apply (./setup/data/styles/[...])",
        required=True
    )

    parser.add_argument(
        "-o", "--output-dir",
        action="store",
        help="Output directory",
        required=False
    )

    args = parser.parse_args()

    # Store style content
    with open(args.style, "r") as file:
        selected_style = json.loads(file.read())

    style.expand(selected_style)
    style.check(selected_style)

    if args.output_dir is None:
        styleName = utils.path.get_last_node(args.style)
        substitutions_dir = f"{configs.SUBSTITUTIONS_DIR}_{styleName}_{time():.0f}"

        # Ensure substitutions directory does not exist already
        i = 2
        while os.path.exists(substitutions_dir):
            substitutions_dir = f"{configs.SUBSTITUTIONS_DIR}_{styleName}_{time():.0f}_{i}"
            i += 1
    else:
        substitutions_dir = args.output_dir

    configs.substitute(selected_style, substitutions_dir)
