import os
import subprocess
import json
import shutil

import setup.lib.printing as printing
import setup.lib.utils as utils

SUBSTITUTIONS_DIR = "./substitutions"
__DOTFILES_DIR = "./dots"
__LINKS_FILE = "./setup/data/links.json"

__SOURCE = "source"
__TARGET = "target"
__FLAGS = "flags"
__SUBS = "subs"
__STYLE_SUBS = "substitutions"
__SUDO_FLAG = "sudo"
__VAR_TARGET_FLAG = "variable-target"

__FIREFOX = "firefox"

with open(__LINKS_FILE, "r") as f:
    __configsList = json.loads(f.read())


def __firefox_target():
    if not os.path.isdir(os.path.expanduser("~/.mozilla")):
        return []

    if not os.path.isdir(os.path.expanduser("~/.mozilla/firefox")):
        return []

    targets = []
    for path in os.listdir(os.path.expanduser("~/.mozilla/firefox")):
        if ".default" in path:
            targets.append(
                f"{os.path.expanduser('~/.mozilla/firefox')}/{path}/chrome/userChrome.css")

    return targets


__TARGET_SEARCH = {
    __FIREFOX: __firefox_target
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
            configTargets = __TARGET_SEARCH[config]()
        else:
            configTargets = __configsList[config][__TARGET]

        if isinstance(configTargets, str):
            configTargets = [configTargets]

        if len(configTargets) == 0:
            printing.colorPrint(
                f"Warning: no targets for {config}", printing.RED)

        for target in configTargets:
            target = target.replace("~", user)

            sourceHash = utils.sha256_checksum(configSource)
            targetHash = None
            if os.path.isfile(target):
                targetHash = utils.sha256_checksum(target)

            # Don't copy if installed config is the same as the new one
            if sourceHash == targetHash:
                printing.colorPrint(
                    f"{utils.get_last_node(configSource):15}",
                    printing.YELLOW,
                    f"({sourceHash[0:4]}...{sourceHash[-4:]})",
                    printing.BLUE,
                    " already installed (",
                    printing.WHITE,
                    target,
                    printing.CYAN,
                    ")",
                    printing.WHITE
                )
                continue

            # Create the directory where the target file needs to be in
            utils.make_dirs(os.path.dirname(target))

            command = ["cp", copyFlags, configSource, target]

            printing.colorPrint(
                f"{utils.get_last_node(configSource):15}",
                printing.YELLOW,
                f"{'-' * 12}> ",
                printing.WHITE,
                target,
                printing.CYAN
            )

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
        if __SUBS in __configsList[config]:
            substitutionIds = __configsList[config][__SUBS]

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
            printing.colorPrint(
                "Varibale target for ",				printing.WHITE,
                f"{link}: could not find target",	printing.RED
            )
            continue

        removeCommand = ["rm", linkTarget]
        if needsSudo:
            removeCommand.insert(0, "sudo")
        if os.path.isfile(linkTarget):
            printing.colorPrint(
                "Removing ",	printing.WHITE,
                linkTarget,		printing.RED
            )
            subprocess.run(removeCommand)
        else:
            printing.colorPrint(
                "Can't find ",	printing.WHITE,
                linkTarget,		printing.RED
            )
