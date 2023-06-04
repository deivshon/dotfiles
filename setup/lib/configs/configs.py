import os
import subprocess
import json
import shutil

import setup.lib.utils as utils

from setup.lib import log
from setup.lib import LIB_DIR
from setup.lib.configs import LINKS_FILE
from setup.lib.configs.targets.firefox import FirefoxVariableTarget

SUBSTITUTIONS_DIR = "./substitutions"
__DOTFILES_DIR = f"{LIB_DIR}/../../dots"

__SOURCE = "source"
__TARGET = "target"
__FLAGS = "flags"
SUBS = "subs"
__STYLE_SUBS = "substitutions"
__SUDO_FLAG = "sudo"
__VAR_TARGET_FLAG = "variable-target"

__FIREFOX = "firefox"

with open(LINKS_FILE, "r") as f:
    __configsList = json.loads(f.read())

__TARGET_SEARCH = {
    __FIREFOX: FirefoxVariableTarget()
}


def link(style, user, keepExpansions=False, force=False):
    copyFlags = "-f" if force else "-i"

    substitute(style, SUBSTITUTIONS_DIR)

    # Handle each link/copy
    for config in __configsList:
        setupFlags = __configsList[config][__FLAGS] if __FLAGS in __configsList[config] else [
        ]
        configSource = os.path.abspath(
            f"{SUBSTITUTIONS_DIR}/{__configsList[config][__SOURCE]}")

        if __VAR_TARGET_FLAG in setupFlags:
            configTargets = __TARGET_SEARCH[config].get_targets()
        else:
            configTargets = __configsList[config][__TARGET]

        if isinstance(configTargets, str):
            configTargets = [configTargets]

        if len(configTargets) == 0:
            log.error(f"Warning: no targets for {config}")

        for target in configTargets:
            target = target.replace("~", user)

            sourceHash = utils.sha256_checksum(configSource)
            targetHash = None
            if os.path.isfile(target):
                targetHash = utils.sha256_checksum(target)

            # Don't copy if installed config is the same as the new one
            if sourceHash == targetHash:
                log.info(
                    f"{log.YELLOW}{utils.get_last_node(configSource):15}{log.BLUE}({sourceHash[0:4]}...{sourceHash[-4:]}){log.NORMAL} already installed ({log.CYAN}{target}{log.NORMAL})")
                continue

            # Create the directory where the target file needs to be in
            utils.make_dirs(os.path.dirname(target))

            command = ["cp", copyFlags, configSource, target]

            log.info(
                f"{log.YELLOW}{utils.get_last_node(configSource):15}{log.NORMAL}{'-' * 12}> {log.CYAN}{target}")

            if __SUDO_FLAG in setupFlags:
                subprocess.run(["sudo"] + command)
            else:
                subprocess.run(command)

    # Delete temporary directory unless the user specified not to
    if not keepExpansions and os.path.isdir(SUBSTITUTIONS_DIR):
        shutil.rmtree(SUBSTITUTIONS_DIR)


def substitute(style, substitutionsDir):
    if not os.path.isdir(substitutionsDir):
        os.mkdir(substitutionsDir)

    # Handle each link/copy
    for config in __configsList:
        configSource = __configsList[config][__SOURCE]

        utils.make_dirs(f"{substitutionsDir}/{os.path.dirname(configSource)}")
        subprocess.run(
            ["cp", f"{__DOTFILES_DIR}/{configSource}", f"{substitutionsDir}/{configSource}"])
        configSource = os.path.abspath(f"{substitutionsDir}/{configSource}")

        substitutionIds = []
        if SUBS in __configsList[config]:
            substitutionIds = __configsList[config][SUBS]

        if len(substitutionIds) > 0:
            # Perform the necessary substitutions using sed
            substitutionVals = style[__STYLE_SUBS]
            for id in substitutionIds:
                subprocess.run(["sed", "-i", "s/" + substitutionIds[id] +
                               "/" + substitutionVals[id] + "/g", configSource])


def remove(user):
    for link in __configsList:
        linkTarget = __configsList[link][__TARGET].replace(
            "~", user) if __FLAGS not in __configsList[link] or __VAR_TARGET_FLAG not in __configsList[link][__FLAGS] else None
        needsSudo = __SUDO_FLAG in __configsList[link][__FLAGS] if __FLAGS in __configsList[link] else False

        if linkTarget is None:
            log.info(
                f"{log.WHITE}Varibale target for {log.RED}{link}: could not find target{log.NORMAL}"
            )
            continue

        removeCommand = ["rm", linkTarget]
        if needsSudo:
            removeCommand.insert(0, "sudo")
        if os.path.isfile(linkTarget):
            log.info(
                f"{log.WHITE}Removing {log.RED}{linkTarget}{log.NORMAL}")
            subprocess.run(removeCommand)
        else:
            log.info(f"{log.WHITE}Can't find {log.RED}{linkTarget}")
