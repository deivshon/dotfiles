import os
import json
import argparse

from time import time
from setup.lib import utils
from setup.lib.config import config
from setup.lib.dots import dots


def main():
    parser = argparse.ArgumentParser(
        prog="substitute",
        description="Perform configs substitutions for a specified color config"
    )

    parser.add_argument(
        "-c", "--config",
        action="store",
        help="Path to file describing the config to apply (./setup/data/configs/[...])",
        required=True
    )

    parser.add_argument(
        "-o", "--output-dir",
        action="store",
        help="Output directory",
        required=False
    )

    args = parser.parse_args()

    # Store config content
    with open(args.config, "r") as file:
        selected_config = json.loads(file.read())

    config.expand(selected_config)
    config.check(selected_config)

    if args.output_dir is None:
        configName = utils.path.get_last_node(args.config)
        substitutions_dir = f"{dots.SUBSTITUTIONS_DIR}_{configName}_{time():.0f}"

        # Ensure substitutions directory does not exist already
        i = 2
        while os.path.exists(substitutions_dir):
            substitutions_dir = f"{dots.SUBSTITUTIONS_DIR}_{configName}_{time():.0f}_{i}"
            i += 1
    else:
        substitutions_dir = args.output_dir

    dots.substitute(selected_config, substitutions_dir)
