import os
import json
import time
import argparse

from setup.lib import log
from setup.lib import utils
from setup.lib.dots import dots
from setup.lib.config import AVAILABLE_CONFIGS, PRESET, config


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
        "-F", "--full",
        action="store_true",
        help="Apply the full setup (use when no DE is installed)"
    )

    parser.add_argument(
        "-o", "--output-dir",
        action="store",
        help="Output directory",
        required=False
    )

    args = parser.parse_args()
    lite = not args.full

    old_cwd = os.getcwd()
    os.chdir(__FILE_DIR)

    if args.config not in AVAILABLE_CONFIGS:
        log.failure(
            f"{log.WHITE}{args.config} is not a valid config{log.NORMAL}\nValid configs: {json.dumps(list(AVAILABLE_CONFIGS.keys()), indent=4)}")

    config_name = args.config
    selected_config = AVAILABLE_CONFIGS[config_name]
    config.initialize(selected_config)

    if PRESET in selected_config:
        config.apply_preset(selected_config, selected_config[PRESET])

    config.apply_defaults(selected_config, lite)
    config.expand(selected_config)
    config.check(selected_config)

    if args.output_dir is None:
        substitutions_dir = os.path.join(
            "..", f"substitutions_{config_name}_{time.time_ns()}")
    else:
        substitutions_dir = args.output_dir

    substitutions_dir = os.path.abspath(substitutions_dir)
    if not os.path.isdir(substitutions_dir):
        utils.path.makedirs(substitutions_dir)

    os.chdir(old_cwd)
    dots.link(selected_config, config_name, lite_mode=False,
              force_copy=True, compilation_map={}, path_prefix=substitutions_dir, run_appliers=False)
