import os
import sys
import json
import argparse

from setup.lib import log
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

    DEFAULT_STYLE = f"{__FILE_DIR__}/data/styles/sunsetDigital.json"

    parser = argparse.ArgumentParser(
        prog="setup",
        description="Setup script for new installations or style changes"
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
        "-s", "--style",
        action="store",
        help="Path to file describing the style to apply (./setup/data/styles/[...])"
    )

    args = parser.parse_args()

    # Check if the script is being run as root
    if os.getuid() == 0:
        sys.exit("Don't run the script as root!")

    current_user = os.path.expanduser("~")
    start_dir = os.getcwd()
    setup_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(setup_dir)

    if not os.path.isfile(SETUP_STATUS):
        setup_status = SetupStatus(
            packages_installed=False,
            post_install_operations=False,
            style=None
        )
    else:
        setup_status = SetupStatus.loads(SETUP_STATUS)

    installed_in_run = False
    if not setup_status.packages_installed:
        install.packages()
        setup_status.packages_installed = True
        installed_in_run = True

    # Imported here because they use modules that are only installed
    # with install.packages
    from setup.lib.configs import configs
    from setup.lib.style import style
    from setup.lib.post import post
    from setup.lib import utils

    if args.remove:
        configs.remove(current_user)
        sys.exit(0)

    if args.style is not None:
        # Style file path argument is relative to caller's cwd (startDir)
        os.chdir(start_dir)
        args.style = os.path.abspath(os.path.expanduser(args.style))
        os.chdir(setup_dir)
        log.info(
            f"{log.WHITE}Selecting style from argument: {log.MAGENTA}{utils.path.get_last_node(args.style)}{log.NORMAL}")
    else:
        if setup_status.style is None:
            log.info(
                f"{log.WHITE}Selecting default style: {log.MAGENTA}{DEFAULT_STYLE}")
            args.style = DEFAULT_STYLE
        else:
            log.info(
                f"{log.WHITE}Selecting style from old setup data ({SETUP_STATUS}): {log.MAGENTA}{utils.path.get_last_node(setup_status.style)}{log.NORMAL}")
            args.style = setup_status.style

    if not os.path.isfile(args.style):
        log.info(f"{log.WHITE}{args.style} does not exist{log.NORMAL}")
        sys.exit(1)

    # Package installation if it's been explicitly requested but not performed
    # because the setup has been run before
    if not installed_in_run and args.packages:
        install.packages()
        setup_status.packages_installed = True

    # Store style content
    with open(args.style, "r") as file:
        selected_style = json.loads(file.read())

    style.expand(selected_style)
    style.check(selected_style)

    DwmInstaller.download()
    PlstatusInstaller.download()
    StInstaller.download()

    configs.link(selected_style, current_user,
                 keep_expansion=args.keep, force=args.force)
    setup_status.style = os.path.abspath(args.style)

    # Download and compile change-vol-pactl
    ChangeVolPactlInstaller.install()

    DwmInstaller.compile()
    StInstaller.compile()

    post.change(selected_style)

    if not setup_status.post_install_operations:
        post.install(selected_style)
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
