import os
import re
import json
import time

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set

from setup.lib import log
from setup.lib import utils
from setup.lib import LIB_DIR
from setup.lib.install.handler import InstallHandler
from setup.lib.dots.appliers.applier import DotApplier
from setup.lib.dots.appliers import APPLIERS, DOT_APPLIERS
from setup.lib.dots.names import BinaryDotsNames, DotsNames
from setup.lib.config import AVAILABLE_CONFIGS, PRESET, config
from setup.lib.dots import BINARY_DOT_LINKS_FILE, DOT_LINKS_FILE
from setup.lib.dots.targets.firefox import FirefoxVariableTarget
from setup.lib.dots.flags import DEVICE_SPECIFIC_FLAG, SUDO_FLAG, VAR_TARGET_FLAG, EXECUTABLE_FLAG


_DOTFILES_DIR = f"{LIB_DIR}/../../dots"
_CONFIG_SUBS = "substitutions"
_FIREFOX = "firefox-userchrome"

_TARGET_SEARCH = {
    _FIREFOX: FirefoxVariableTarget()
}


def _log_already_installed(hash_digest: str, target: str) -> None:
    log.info(
        f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.RED}already installed{log.NORMAL} {log.YELLOW}{target}{log.NORMAL}")


def _log_installed(hash_digest: str, target: str, installed_once: bool) -> None:
    if installed_once:
        log.info(
            f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.GREEN}only ever install{log.NORMAL} {log.YELLOW}{target}")
    else:
        log.info(
            f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.GREEN}installed in path{log.NORMAL} {log.YELLOW}{target}")


@dataclass
class _DotLink():
    name: str
    source: str
    target: Optional[str] = None
    subs: Dict[str, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    dot_applier: Optional[DotApplier] = None


@dataclass
class _DotApplyCommand:
    force_copy: bool
    content: str | bytes
    needs_sudo: bool
    executable: bool

    def run(self, target: str):
        if os.path.isfile(target) and utils.hash.sha512_file(target) not in _DOTFILES_HASHES:
            backup_target = os.path.join(os.path.dirname(
                target), f"{time.time_ns()}_{os.path.basename(target)}.bkp")

            utils.path.copy(target, backup_target, force=True,
                            needs_sudo=self.needs_sudo)
            utils.path.make_non_executable(backup_target, sudo=self.needs_sudo)

        utils.path.write_to_file(self.content, target, force=self.force_copy,
                                 needs_sudo=self.needs_sudo)
        if self.executable:
            utils.path.make_executable(target, sudo=self.needs_sudo)


@dataclass
class _BinaryDotLink():
    name: str
    target: str
    flags: List[str]
    content: bytes

    def __init__(self, dot_link: _DotLink):
        if dot_link.target is None:
            raise InvalidDotLink

        self.target = os.path.abspath(
            dot_link.target.replace("~", utils.HOME_DIR))
        self.name = dot_link.name
        self.flags = dot_link.flags

        source = f"{_DOTFILES_DIR}/{dot_link.source}"
        if not os.path.isfile(source):
            raise InvalidDotLink
        with open(source, "rb") as f:
            self.content = f.read()

    def apply(self, force_copy: bool, path_prefix: Optional[str] = None):
        target = self.target
        if path_prefix is not None:
            target = f"{path_prefix}{target}"

        needs_sudo = SUDO_FLAG in self.flags
        content_hash = utils.hash.sha512(self.content)
        target_hash = None
        if os.path.isfile(target):
            target_hash = utils.hash.sha512_file(target)

        if content_hash == target_hash:
            _log_already_installed(content_hash, target)
            return

        target_dir = os.path.dirname(target)
        if not os.path.isdir(target_dir):
            utils.path.makedirs(target_dir)
        apply_command = _DotApplyCommand(
            force_copy, self.content, needs_sudo, executable=False)
        apply_command.run(target)

        _log_installed(content_hash, target, installed_once=False)


class InvalidDotLink(Exception):
    pass


class InvalidComputedDotLink(Exception):
    pass


_CONFIGS: Dict[str, Dict] = {}
for config_name in AVAILABLE_CONFIGS:
    selected_config = AVAILABLE_CONFIGS[config_name]
    config.initialize(selected_config)

    if PRESET in selected_config:
        config.apply_preset(
            selected_config, selected_config[PRESET])

    config.apply_defaults(selected_config)
    config.expand(selected_config)
    config.check(selected_config)
    _CONFIGS[config_name] = selected_config


class _ComputedDotLink():
    name: str
    targets: List[str]
    flags: List[str]
    content: Dict[str, str] | str

    def __init__(self, dot_link: _DotLink):
        self.name = dot_link.name
        self.flags = dot_link.flags
        if VAR_TARGET_FLAG in self.flags:
            self.targets = _TARGET_SEARCH[dot_link.name].get_targets()
        elif dot_link.target is None or not isinstance(dot_link.target, str):
            raise InvalidDotLink
        else:
            self.targets = [dot_link.target]

        if len(self.targets) == 0:
            log.error(f"Could not find any target for {self.targets}")
            return

        source = f"{_DOTFILES_DIR}/{dot_link.source}"
        if not os.path.isfile(source):
            raise InvalidDotLink

        with open(source, "r") as f:
            base_content = f.read()

        if len(dot_link.subs) == 0:
            self.content = base_content
            if dot_link.dot_applier is not None:
                log.info(
                    f"Running dot applier {log.GREEN}{dot_link.dot_applier.name}")
                self.content = dot_link.dot_applier.run(self.content)
                print("\n", end="")
        else:
            self.content = {}
            for config_name in _CONFIGS:
                selected_config = _CONFIGS[config_name]

                substitution_vals = selected_config[_CONFIG_SUBS]
                current_content = base_content
                for key in dot_link.subs:
                    current_content = re.sub(
                        dot_link.subs[key], substitution_vals[key], current_content)

                if dot_link.dot_applier is not None:
                    log.info(
                        f"Running dot applier {log.GREEN}{dot_link.dot_applier.name}")
                    current_content = dot_link.dot_applier.run(current_content)
                    print("\n", end="")

                self.content[config_name] = current_content

    def apply(self, config_name: str, force_copy: bool, compilation_map: Dict[str, InstallHandler], path_prefix: Optional[str] = None) -> None:
        for target in self.targets:
            self.__apply_single_target(
                target, config_name, force_copy, compilation_map, path_prefix)

    def __apply_single_target(self, target: str, config_name: str, force_copy: bool, compilation_map: Dict[str, InstallHandler], path_prefix: Optional[str]) -> None:
        executable = EXECUTABLE_FLAG in self.flags
        needs_sudo = SUDO_FLAG in self.flags
        device_specific = DEVICE_SPECIFIC_FLAG in self.flags

        target = os.path.abspath(target.replace("~", utils.HOME_DIR))
        if path_prefix is not None:
            target = f"{path_prefix}{target}"

        if os.path.isfile(target) and device_specific:
            return

        if isinstance(self.content, str):
            content = self.content
        else:
            content = self.content[config_name]

        content_hash = utils.hash.sha512(content)

        target_hash: Optional[str] = None
        if os.path.isfile(target):
            target_hash = utils.hash.sha512_file(target)

        if content_hash == target_hash:
            _log_already_installed(content_hash, target)
            return

        if not os.path.isdir(os.path.dirname(target)):
            utils.path.makedirs(os.path.dirname(target))

        apply_command = _DotApplyCommand(
            force_copy, content, needs_sudo, executable)
        apply_command.run(target)

        if device_specific:
            _log_installed(content_hash, target, installed_once=True)
        else:
            _log_installed(content_hash, target, installed_once=False)

        if self.name in compilation_map:
            compilation_map[self.name].needsCompilation = True


def link(config, config_name: str, force_copy=False, compilation_map: Dict[str, InstallHandler] = {}, path_prefix: Optional[str] = None, run_appliers: bool = True):
    print("\n", end="")
    for computed_link in _COMPUTED_DOT_LINKS:
        computed_link.apply(config_name, force_copy,
                            compilation_map, path_prefix)

    for binary_link in _BINARY_DOT_LINKS:
        binary_link.apply(force_copy, path_prefix)

    print("\n", end="")

    if run_appliers:
        for applier in APPLIERS:
            log.info(f"Running applier {log.GREEN}{applier.name}")
            applier.run(config[_CONFIG_SUBS])

    print("\n", end="")


def __get_all_hashes() -> Set[str]:
    hashes = set()
    for computed_link in _COMPUTED_DOT_LINKS:
        if isinstance(computed_link.content, str):
            hashes.add(utils.hash.sha512(computed_link.content))
        else:
            for config_name in computed_link.content:
                config_content = computed_link.content[config_name]
                hashes.add(utils.hash.sha512(config_content))

    for binary_link in _BINARY_DOT_LINKS:
        hashes.add(utils.hash.sha512(binary_link.content))

    return hashes


def __compute_dot_links() -> List[_ComputedDotLink]:
    computed: List[_ComputedDotLink] = []
    with open(DOT_LINKS_FILE, "r") as file:
        __links_dict = json.loads(file.read())
        for key in __links_dict:
            if key not in DotsNames.__dict__.values():
                log.failure(
                    f"Naming inconsistency: \"{key}\" does not appear in allowed names")

            dot_link = _DotLink(
                name=key, **__links_dict[key], dot_applier=DOT_APPLIERS[key] if key in DOT_APPLIERS else None)
            computed.append(_ComputedDotLink(dot_link))
    return computed


def __binary_dot_links() -> List[_BinaryDotLink]:
    binary_links: List[_BinaryDotLink] = []
    with open(BINARY_DOT_LINKS_FILE, "r") as file:
        __binary_links_dict = json.loads(file.read())
        for key in __binary_links_dict:
            if key not in BinaryDotsNames.__dict__.values():
                log.failure(
                    f"Naming inconsistency: \"{key}\" does not appear in allowed names")

            if key in DOT_APPLIERS:
                log.failure(
                    "Binary dot links can't have a related dot applier")

            dot_link = _DotLink(
                name=key, **__binary_links_dict[key], dot_applier=None)
            binary_links.append(_BinaryDotLink(dot_link))
    return binary_links


_COMPUTED_DOT_LINKS = __compute_dot_links()
_BINARY_DOT_LINKS = __binary_dot_links()
_DOTFILES_HASHES = __get_all_hashes()
