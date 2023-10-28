import os
import sys
import json
import argparse
from typing import Dict, List

from setup.lib import log
from setup.lib.post import post
from setup.lib.dots import dots
from setup.lib.config import PRESET, config
from setup.lib.install import install
from setup.lib.dots.names import DotsNames
from setup.lib.install.st import StInstaller
from setup.lib.install.dwm import DwmInstaller
from setup.lib.config import AVAILABLE_CONFIGS
from setup.lib.install.handler import InstallHandler
from setup.lib.status import SetupStatus, SETUP_STATUS
from setup.lib.install.alias_rs import AliasRsInstaller
from setup.lib.install.plstatus import PlstatusInstaller
from setup.lib.install.command_cache import CommandCacheInstaller
from setup.lib.install.status_scripts import StatusScriptsInstaller
from setup.lib.install.change_vol_pactl import ChangeVolPactlInstaller

from setup.lib import symlinks


def main():
    dwm_installer = DwmInstaller()

    installers: List[InstallHandler] = [
        dwm_installer,
        PlstatusInstaller(),
        StInstaller(),
        ChangeVolPactlInstaller(),
        CommandCacheInstaller(),
        StatusScriptsInstaller(),
        AliasRsInstaller(),
    ]

    compilationMap: Dict[str, InstallHandler] = {
        DotsNames.DWM_CONFIG: dwm_installer,
    }

    __FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_CONFIG = "sunset-yellow-digital"

    parser = argparse.ArgumentParser(
        prog="setup",
        description="Setup script for new installations or config changes"
    )

    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing configuration targets without asking"
    )
    parser.add_argument(
        "-k", "--keep",
        action="store_true",
        help="Keep directory containing expanded configurations"
    )
    parser.add_argument(
        "-rm", "--remove",
        action="store_true",
        help="Remove existing configuration files"
    )
    parser.add_argument(
        "-p", "--packages",
        action="store_true",
        help="Force packages installation"
    )
    parser.add_argument(
        "-c", "--config",
        action="store",
        help="Name of the config to apply"
    )

    parser.add_argument(
        "-g", "--git-pull",
        action="store_true",
        help="If repositories of installed custom software already exist, pull"
    )

    args = parser.parse_args()

    if os.getuid() == 0:
        log.failure("Don't run the script as root!")

    homedir = os.path.expanduser("~")
    os.chdir(__FILE_DIR)

    if not os.path.isfile(SETUP_STATUS):
        setup_status = SetupStatus(
            packages_installed=False,
            post_install_operations=False,
            config=None
        )
    else:
        setup_status = SetupStatus.loads(SETUP_STATUS)

    if args.config is not None:
        log.info(
            f"{log.WHITE}Selecting config from argument: {log.BLUE}{args.config}{log.NORMAL}")
    else:
        if setup_status.config is None:
            log.info(
                f"{log.WHITE}Selecting default config: {log.BLUE}{DEFAULT_CONFIG}")
            args.config = DEFAULT_CONFIG
        else:
            log.info(
                f"{log.WHITE}Selecting config from old setup data ({SETUP_STATUS}): {log.BLUE}{setup_status.config}{log.NORMAL}")
            args.config = setup_status.config

    if args.config not in AVAILABLE_CONFIGS:
        log.failure(
            f"{log.WHITE}{args.config} is not a valid config{log.NORMAL}\nValid configs: {json.dumps(list(AVAILABLE_CONFIGS.keys()), indent=4)}")

    selected_config = AVAILABLE_CONFIGS[args.config]
    config.initialize(selected_config)

    if PRESET in selected_config:
        config.apply_preset(selected_config, selected_config[PRESET])

    config.apply_defaults(selected_config)
    config.expand(selected_config)
    config.check(selected_config)

    installed_in_run = False
    if not setup_status.packages_installed:
        install.pacman_packages()
        post.after_packages_install(selected_config)
        install.paru_packages()
        setup_status.packages_installed = True
        installed_in_run = True

    if args.remove:
        symlinks.remove()
        dots.remove(homedir)
        sys.exit(0)

    # Package installation if it's been explicitly requested but not performed
    # because the setup has been run before
    if not installed_in_run and args.packages:
        install.pacman_packages()
        install.paru_packages()
        setup_status.packages_installed = True

    for inst in installers:
        inst.download(args.git_pull)

    dots.link(selected_config, homedir,
              keep_expansion=args.keep,
              force=args.force,
              compilationMap=compilationMap)

    setup_status.config = args.config

    post.change(selected_config)

    if not setup_status.post_install_operations:
        post.install(selected_config)
        setup_status.post_install_operations = True

    os.environ["PATH"] += ":" + os.path.expanduser("~/.local/scripts")
    for inst in installers:
        inst.compile()

    symlinks.apply()

    with open(SETUP_STATUS, "w") as file:
        file.write(setup_status.dumps())
