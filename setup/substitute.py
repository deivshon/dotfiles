import os
import argparse

from time import time
from setup.lib.dots import dots
from setup.lib import log
from setup.lib.config import AVAILABLE_CONFIGS, config


def main():
    __FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(
        prog="substitute",
        description="Perform configs substitutions for a specified color config"
    )

    parser.add_argument(
        "-c", "--config",
        action="store",
        help="Name of the config to apply",
        required=True
    )

    parser.add_argument(
        "-o", "--output-dir",
        action="store",
        help="Output directory",
        required=False
    )

    args = parser.parse_args()

    old_cwd = os.getcwd()
    os.chdir(__FILE_DIR)

    # Store config content
    if args.config not in AVAILABLE_CONFIGS:
        log.failure("Select a valid config")

    selected_config = AVAILABLE_CONFIGS[args.config]

    config.apply_defaults(selected_config)
    config.expand(selected_config)
    config.check(selected_config)

    if args.output_dir is None:
        substitutions_dir = f"{dots.SUBSTITUTIONS_DIR}_{args.config}_{time():.0f}"

        # Ensure substitutions directory does not exist already
        i = 2
        while os.path.exists(substitutions_dir):
            substitutions_dir = f"{dots.SUBSTITUTIONS_DIR}_{args.config}_{time():.0f}_{i}"
            i += 1
    else:
        substitutions_dir = args.output_dir

    os.chdir(old_cwd)
    dots.substitute(selected_config, substitutions_dir)
