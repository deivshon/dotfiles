import os
import json
import time
import shutil
import subprocess

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.dots import LINKS_FILE, LINK_SUBS, SUBSTITUTIONS_DIR
from setup.lib.dots.names import DotsNames
from setup.lib.utils.path import replace_in_file
from setup.lib.install.handler import InstallHandler
from setup.lib.dots.appliers.applier import DotApplier
from setup.lib.dots.appliers import APPLIERS, DOT_APPLIERS
from setup.lib.dots.targets.firefox import FirefoxVariableTarget
from setup.lib.config import AVAILABLE_CONFIGS, PRESET, config
from setup.lib.dots.flags import DEVICE_SPECIFIC_FLAG, SUDO_FLAG, VAR_TARGET_FLAG, EXECUTABLE_FLAG


__DOTFILES_DIR = f"{LIB_DIR}/../../dots"
__CONFIG_SUBS = "substitutions"
__FIREFOX = "firefox-userchrome"


@dataclass
class DotLink:
    name: str
    source: str
    target: Optional[str] = None
    subs: Dict[str, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    dot_applier: Optional[DotApplier] = None


@dataclass
class __DotCopyCommand:
    force_copy: bool
    source: str
    needs_sudo: bool
    executable: bool

    def run(self, target: str):
        if os.path.isfile(target) and not utils.hash.sha512(target) in DOTFILES_HASHES:
            backup_target = os.path.join(os.path.dirname(
                target), f"{time.time_ns()}_{os.path.basename(target)}.bkp")

            utils.path.copy(target, backup_target, force=True,
                            needs_sudo=self.needs_sudo)
            utils.path.make_non_executable(backup_target, sudo=self.needs_sudo)

        utils.path.copy(self.source, target, force=self.force_copy,
                        needs_sudo=self.needs_sudo)
        if self.executable:
            utils.path.make_executable(target, sudo=self.needs_sudo)


class InvalidDotLink(Exception):
    pass


__DOT_LINKS: List[DotLink] = []

with open(LINKS_FILE, "r") as file:
    __configs_list = json.loads(file.read())
    for key in __configs_list:
        if key not in DotsNames.__dict__.values():
            log.failure(
                f"Naming inconsistency: \"{key}\" does not appear in allowed names")

        __DOT_LINKS.append(DotLink(
            name=key, **__configs_list[key], dot_applier=DOT_APPLIERS[key] if key in DOT_APPLIERS else None))

__TARGET_SEARCH = {
    __FIREFOX: FirefoxVariableTarget()
}


def link(config, keep_expansion=False, force_copy=False, compilationMap: Dict[str, InstallHandler] = {}):
    substitute(config, SUBSTITUTIONS_DIR, run_appliers=True)

    no_target_dots = []

    print("\n", end="")
    for dot_link in __DOT_LINKS:
        if VAR_TARGET_FLAG in dot_link.flags:
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
            __link_single_target(dot_link, target, compilationMap, force_copy)

    if not keep_expansion and os.path.isdir(SUBSTITUTIONS_DIR):
        shutil.rmtree(SUBSTITUTIONS_DIR)

    print("\n", end="")
    for target in no_target_dots:
        log.error(f"Could not find any target for {target}")

    for applier in APPLIERS:
        log.info(f"Running applier {log.GREEN}{applier.name}")
        applier.run(config[__CONFIG_SUBS])

    print("\n", end="")


def __link_single_target(dot_link: DotLink, target: str, compilationMap: Dict[str, InstallHandler], force_copy: bool):
    source = os.path.abspath(
        f"{SUBSTITUTIONS_DIR}/{dot_link.source}")
    device_specific = DEVICE_SPECIFIC_FLAG in dot_link.flags
    executable = EXECUTABLE_FLAG in dot_link.flags
    needs_sudo = SUDO_FLAG in dot_link.flags

    target = target.replace("~", utils.HOME_DIR)

    if device_specific and os.path.exists(target):
        return

    source_hash = utils.hash.sha512(source)
    target_hash = None
    if os.path.isfile(target):
        target_hash = utils.hash.sha512(target)

    if source_hash == target_hash:
        log.info(
            f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.RED}already installed{log.NORMAL} {log.YELLOW}{target}{log.NORMAL}")
        return

    if not os.path.isdir(os.path.dirname(target)):
        utils.path.makedirs(os.path.dirname(target))

    copy_command = __DotCopyCommand(force_copy, source, needs_sudo, executable)
    copy_command.run(target)

    if device_specific:
        log.info(
            f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.GREEN}only ever install{log.NORMAL} {log.YELLOW}{target}")
    else:
        log.info(
            f"{log.BLUE}{source_hash[0:4]}...{source_hash[-4:]}{log.NORMAL} | {log.GREEN}installed in path{log.NORMAL} {log.YELLOW}{target}")

    if dot_link.name in compilationMap:
        compilationMap[dot_link.name].needsCompilation = True


def substitute(config, substitutions_dir, run_appliers: bool = True):
    if not os.path.isdir(substitutions_dir):
        os.makedirs(substitutions_dir)

    for dot_link in __DOT_LINKS:
        source = dot_link.source
        config_dir = f"{substitutions_dir}/{os.path.dirname(source)}"
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        utils.path.copy(f"{__DOTFILES_DIR}/{source}",
                        f"{substitutions_dir}/{source}", force=True, needs_sudo=False)
        source = os.path.abspath(f"{substitutions_dir}/{source}")

        subs = dot_link.subs
        if len(subs) > 0:
            substitution_vals = config[__CONFIG_SUBS]
            for id in subs:
                replace_in_file(source, subs[id], substitution_vals[id])

        if run_appliers and dot_link.dot_applier is not None:
            log.info(
                f"Running dot applier {log.GREEN}{dot_link.dot_applier.name}")
            dot_link.dot_applier.run(source)


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


def __get_config_hashes(selected_config: Dict) -> Set[str]:
    config.initialize(selected_config)

    if PRESET in selected_config:
        config.apply_preset(selected_config, selected_config[PRESET])

    config.apply_defaults(selected_config)
    config.expand(selected_config)
    config.check(selected_config)

    target_dir = os.path.join("/tmp", f"subs-{time.time_ns()}")
    substitute(selected_config, target_dir, False)

    hashes = utils.hash.file_hashes(target_dir)
    shutil.rmtree(target_dir)

    return hashes


DOTFILES_HASHES = set()
log.info("Creating hashes for backups necessity checking")
for selected_config in AVAILABLE_CONFIGS:
    DOTFILES_HASHES = DOTFILES_HASHES.union(
        __get_config_hashes(AVAILABLE_CONFIGS[selected_config]))
print("\n", end="")
