import os
import subprocess
import json
import shutil
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.dots import LINKS_FILE
from setup.lib.dots.targets.firefox import FirefoxVariableTarget
from setup.lib.dots.flags import DEVICE_SPECIFIC_FLAG, SUDO_FLAG, VAR_TARGET_FLAG, EXECUTABLE_FLAG
from setup.lib.install.handler import InstallHandler


SUBSTITUTIONS_DIR = "./substitutions"
__DOTFILES_DIR = f"{LIB_DIR}/../../dots"

SUBS = "subs"
__CONFIG_SUBS = "substitutions"


__FIREFOX = "firefox-userchrome"


@dataclass
class DotLink:
    name: str
    source: str
    target: Optional[str] = None
    subs: Dict[str, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)


class InvalidDotLink(Exception):
    pass


__DOT_LINKS: List[DotLink] = []

with open(LINKS_FILE, "r") as file:
    __configs_list = json.loads(file.read())
    for key in __configs_list:
        __DOT_LINKS.append(DotLink(name=key, **__configs_list[key]))

__TARGET_SEARCH = {
    __FIREFOX: FirefoxVariableTarget()
}


def link(config, user, keep_expansion=False, force=False, compilationMap: Dict[str, InstallHandler] = {}):
    copy_flags = "-f" if force else "-i"

    substitute(config, SUBSTITUTIONS_DIR)

    no_target_dots = []

    for dot_link in __DOT_LINKS:
        source = os.path.abspath(
            f"{SUBSTITUTIONS_DIR}/{dot_link.source}")
        flags = dot_link.flags

        device_specific = DEVICE_SPECIFIC_FLAG in flags

        if VAR_TARGET_FLAG in flags:
            targets = __TARGET_SEARCH[dot_link.name].get_targets()
        elif dot_link.target is not None:
            targets = dot_link.target
        else:
            raise InvalidDotLink

        if isinstance(targets, str):
            targets = [targets]

        if len(targets) == 0:
            no_target_dots.append(dot_link.name)

        for target in targets:
            target = target.replace("~", user)

            if device_specific and os.path.exists(target):
                continue

            source_hash = utils.hash.sha256_checksum(source)
            target_hash = None
            if os.path.isfile(target):
                target_hash = utils.hash.sha256_checksum(target)

            if source_hash == target_hash:
                log.info(
                    f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.RED}already installed{log.NORMAL} {log.YELLOW}{target}{log.NORMAL}")
                continue

            if not os.path.isdir(os.path.dirname(target)):
                utils.path.makedirs(os.path.dirname(target))

            command = ["cp", copy_flags, source, target]

            if SUDO_FLAG in flags:
                subprocess.run(["sudo"] + command)
            else:
                subprocess.run(command)

            if device_specific:
                log.info(
                    f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.GREEN}only ever install{log.NORMAL} {log.YELLOW}{target}")
            else:
                log.info(
                    f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.GREEN}installed in path{log.NORMAL} {log.YELLOW}{target}")

            if EXECUTABLE_FLAG in flags:
                utils.path.make_executable(target, sudo=SUDO_FLAG in flags)

            if dot_link.name in compilationMap:
                compilationMap[dot_link.name].needsCompilation = True

    if not keep_expansion and os.path.isdir(SUBSTITUTIONS_DIR):
        shutil.rmtree(SUBSTITUTIONS_DIR)

    for target in no_target_dots:
        log.error(f"Could not find any target for {target}")


def substitute(config, substitutions_dir):
    if not os.path.isdir(substitutions_dir):
        os.makedirs(substitutions_dir)

    for dot_link in __DOT_LINKS:
        source = dot_link.source
        config_dir = f"{substitutions_dir}/{os.path.dirname(source)}"
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        subprocess.run(
            ["cp", f"{__DOTFILES_DIR}/{source}", f"{substitutions_dir}/{source}"])
        source = os.path.abspath(f"{substitutions_dir}/{source}")

        subs = dot_link.subs
        if len(subs) > 0:
            substitution_vals = config[__CONFIG_SUBS]
            for id in subs:
                subprocess.run(["sed", "-i", "s/" + subs[id] +
                               "/" + substitution_vals[id] + "/g", source])


def remove(homedir):
    for dot_link in __DOT_LINKS:
        flags = dot_link.flags

        if VAR_TARGET_FLAG in flags:
            link_targets = __TARGET_SEARCH[dot_link.name].get_targets()
        elif dot_link.target is not None:
            link_targets = dot_link.target.replace(
                "~", homedir)
        else:
            link_targets = []

        if not isinstance(link_targets, list):
            link_targets = [link_targets]

        needs_sudo = SUDO_FLAG in dot_link.flags

        if len(link_targets) == 0:
            log.info(
                f"{log.WHITE}Variable target for {log.RED}{dot_link}: could not find target{log.NORMAL}"
            )
            continue

        for target in link_targets:
            remove_command = ["rm", target]
            if needs_sudo:
                remove_command.insert(0, "sudo")

            if os.path.isfile(target):
                subprocess.run(remove_command)
                log.info(
                    f"{log.WHITE}Removed {log.RED}{target}{log.NORMAL}")
            else:
                log.info(f"{log.WHITE}Can't find {log.RED}{target}")
