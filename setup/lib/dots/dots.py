import os
import subprocess
import json
import shutil

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.dots import LINKS_FILE
from setup.lib.dots.targets.firefox import FirefoxVariableTarget

SUBSTITUTIONS_DIR = "./substitutions"
__DOTFILES_DIR = f"{LIB_DIR}/../../dots"

__SOURCE = "source"
__TARGET = "target"
__FLAGS = "flags"
SUBS = "subs"
__CONFIG_SUBS = "substitutions"
__SUDO_FLAG = "sudo"
__VAR_TARGET_FLAG = "variable-target"

__FIREFOX = "firefox"

with open(LINKS_FILE, "r") as file:
    __configs_list = json.loads(file.read())

__TARGET_SEARCH = {
    __FIREFOX: FirefoxVariableTarget()
}


def link(config, user, keep_expansion=False, force=False):
    copy_flags = "-f" if force else "-i"

    substitute(config, SUBSTITUTIONS_DIR)

    no_target_dots = []
    # Handle each link/copy
    for dot_link in __configs_list:
        setup_flags = __configs_list[dot_link][__FLAGS] if __FLAGS in __configs_list[dot_link] else [
        ]
        config_source = os.path.abspath(
            f"{SUBSTITUTIONS_DIR}/{__configs_list[dot_link][__SOURCE]}")

        if __VAR_TARGET_FLAG in setup_flags:
            config_targets = __TARGET_SEARCH[dot_link].get_targets()
        else:
            config_targets = __configs_list[dot_link][__TARGET]

        if isinstance(config_targets, str):
            config_targets = [config_targets]

        if len(config_targets) == 0:
            no_target_dots.append(dot_link)

        for target in config_targets:
            target = target.replace("~", user)

            source_hash = utils.hash.sha256_checksum(config_source)
            target_hash = None
            if os.path.isfile(target):
                target_hash = utils.hash.sha256_checksum(target)

            # Don't copy if installed dot is the same as the new one
            if source_hash == target_hash:
                log.info(
                    f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.RED}already installed{log.NORMAL} {log.YELLOW}{target}{log.NORMAL}")
                continue

            if not os.path.isdir(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))

            command = ["cp", copy_flags, config_source, target]

            log.info(
                f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.GREEN}installed in path{log.NORMAL} {log.YELLOW}{target}")

            if __SUDO_FLAG in setup_flags:
                subprocess.run(["sudo"] + command)
            else:
                subprocess.run(command)

    if not keep_expansion and os.path.isdir(SUBSTITUTIONS_DIR):
        shutil.rmtree(SUBSTITUTIONS_DIR)

    for target in no_target_dots:
        log.error(f"Could not find any target for {target}")


def substitute(config, substitutions_dir):
    if not os.path.isdir(substitutions_dir):
        os.mkdir(substitutions_dir)

    # Handle each link/copy
    for dot_link in __configs_list:
        config_source = __configs_list[dot_link][__SOURCE]
        config_dir = f"{substitutions_dir}/{os.path.dirname(config_source)}"
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        subprocess.run(
            ["cp", f"{__DOTFILES_DIR}/{config_source}", f"{substitutions_dir}/{config_source}"])
        config_source = os.path.abspath(f"{substitutions_dir}/{config_source}")

        substitution_ids = []
        if SUBS in __configs_list[dot_link]:
            substitution_ids = __configs_list[dot_link][SUBS]

        if len(substitution_ids) > 0:
            # Perform the necessary substitutions using sed
            substitution_vals = config[__CONFIG_SUBS]
            for id in substitution_ids:
                subprocess.run(["sed", "-i", "s/" + substitution_ids[id] +
                               "/" + substitution_vals[id] + "/g", config_source])


def remove(user):
    for link in __configs_list:
        link_target = __configs_list[link][__TARGET].replace(
            "~", user) if __FLAGS not in __configs_list[link] or __VAR_TARGET_FLAG not in __configs_list[link][__FLAGS] else None
        needs_sudo = __SUDO_FLAG in __configs_list[link][__FLAGS] if __FLAGS in __configs_list[link] else False

        if link_target is None:
            log.info(
                f"{log.WHITE}Variable target for {log.RED}{link}: could not find target{log.NORMAL}"
            )
            continue

        remove_command = ["rm", link_target]
        if needs_sudo:
            remove_command.insert(0, "sudo")
        if os.path.isfile(link_target):
            log.info(
                f"{log.WHITE}Removing {log.RED}{link_target}{log.NORMAL}")
            subprocess.run(remove_command)
        else:
            log.info(f"{log.WHITE}Can't find {log.RED}{link_target}")
