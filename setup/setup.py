import os
import sys
import json
import argparse

from setup.lib import log
from setup.lib import utils
from setup.lib.post import post
from setup.lib.config import config
from setup.lib.dots import dots

from setup.lib.status import SetupStatus, SETUP_STATUS
from setup.lib.install import install
from setup.lib.install.dwm import DwmInstaller
from setup.lib.install.change_vol_pactl import ChangeVolPactlInstaller
from setup.lib.install.command_cache import CommandCacheInstaller
from setup.lib.install.plstatus import PlstatusInstaller
from setup.lib.install.st import StInstaller
from setup.lib.install.status_scripts import StatusScriptsInstaller


def main():
    __FILE_DIR__ = os.path.dirname(os.path.realpath(__file__))

    DEFAULT_CONFIG = f"{__FILE_DIR__}/data/configs/sunsetDigital.json"

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
        help="Path to file describing the config to apply (./setup/data/configs/[...])"
    )

    args = parser.parse_args()

    if os.getuid() == 0:
        log.failure("Don't run the script as root!")

    current_user = os.path.expanduser("~")
    start_dir = os.getcwd()
    setup_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(setup_dir)

    if not os.path.isfile(SETUP_STATUS):
        setup_status = SetupStatus(
            packages_installed=False,
            post_install_operations=False,
            config=None
        )
    else:
        setup_status = SetupStatus.loads(SETUP_STATUS)

    installed_in_run = False
    if not setup_status.packages_installed:
        install.packages()
        setup_status.packages_installed = True
        installed_in_run = True

    if args.remove:
        dots.remove(current_user)
        sys.exit(0)

    if args.config is not None:
        # Config file path argument is relative to caller's cwd (startDir)
        os.chdir(start_dir)
        args.config = os.path.abspath(os.path.expanduser(args.config))
        os.chdir(setup_dir)
        log.info(
            f"{log.WHITE}Selecting config from argument: {log.BLUE}{utils.path.get_last_node(args.config)}{log.NORMAL}")
    else:
        if setup_status.config is None:
            log.info(
                f"{log.WHITE}Selecting default config: {log.BLUE}{DEFAULT_CONFIG}")
            args.config = DEFAULT_CONFIG
        else:
            log.info(
                f"{log.WHITE}Selecting config from old setup data ({SETUP_STATUS}): {log.BLUE}{utils.path.get_last_node(setup_status.config)}{log.NORMAL}")
            args.config = setup_status.config

    if not os.path.isfile(args.config):
        log.failure(f"{log.WHITE}{args.config} does not exist{log.NORMAL}")

    # Package installation if it's been explicitly requested but not performed
    # because the setup has been run before
    if not installed_in_run and args.packages:
        install.packages()
        setup_status.packages_installed = True

    # Store config content
    with open(args.config, "r") as file:
        selected_config = json.loads(file.read())

    config.expand(selected_config)
    config.check(selected_config)

    DwmInstaller.download()
    PlstatusInstaller.download()
    StInstaller.download()

    dots.link(selected_config, current_user,
              keep_expansion=args.keep, force=args.force)
    setup_status.config = os.path.abspath(args.config)

    # Download and compile change-vol-pactl
    ChangeVolPactlInstaller.install()

    DwmInstaller.compile()
    StInstaller.compile()

    post.change(selected_config)

    if not setup_status.post_install_operations:
        post.install(selected_config)
        setup_status.post_install_operations = True

    # Install Rust programs after rust is configured,
    # which happens only during the post install operations
    CommandCacheInstaller.install()

    StatusScriptsInstaller.install()
    os.environ["PATH"] += ":" + os.path.expanduser("~/.local/scripts")

    # Compile plstatus after status scripts are installed,
    # otherwise commands in plstatus configuration will not exists in PATH
    # at compile time and compilation will subsequently fail
    PlstatusInstaller.compile()

    with open(SETUP_STATUS, "w") as file:
        file.write(setup_status.dumps())
