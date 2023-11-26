import os
import json

from typing import Dict, List, Optional, Set

from setup.lib import log, utils
from setup.lib.config import CONFIGS
from setup.lib.const.dots import DOT_LINKS_FILE
from setup.lib.dots.appliers import DOT_APPLIERS
from setup.lib.dots import DOTFILES_DIR, TARGET_SEARCH
from setup.lib.const.config import CONFIG_SUBSTITUTIONS
from setup.lib.dots.apply_command import DotApplyCommand
from setup.lib.dots.dot_link import _DotLink, InvalidDotLink
from setup.lib.dots.dots_log import dot_log_already_installed, dot_log_installed

from setup.lib.dots.names import DotsNames
from setup.lib.install.handler import InstallHandler
from setup.lib.dots.flags import DEVICE_SPECIFIC_FLAG, SUDO_FLAG, VAR_TARGET_FLAG, EXECUTABLE_FLAG


class _ComputedDotLink():
    name: str
    targets: List[str]
    flags: List[str]
    content: Dict[str, str] | str

    def __init__(self, dot_link: _DotLink):
        self.name = dot_link.name
        self.flags = dot_link.flags
        if VAR_TARGET_FLAG in self.flags:
            self.targets = TARGET_SEARCH[dot_link.name].get_targets()
        elif dot_link.target is None or not isinstance(dot_link.target, str):
            raise InvalidDotLink
        else:
            self.targets = [dot_link.target]

        if len(self.targets) == 0:
            log.error(f"Could not find any target for {self.name}")

        source = f"{DOTFILES_DIR}/{dot_link.source}"
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
            for config_name in CONFIGS:
                selected_config = CONFIGS[config_name]

                substitution_vals = selected_config[CONFIG_SUBSTITUTIONS]
                current_content = base_content
                for key in dot_link.subs:
                    current_content = current_content.replace(
                        dot_link.subs[key], substitution_vals[key])

                if dot_link.dot_applier is not None:
                    log.info(
                        f"Running dot applier {log.GREEN}{dot_link.dot_applier.name}")
                    current_content = dot_link.dot_applier.run(current_content)
                    print("\n", end="")

                self.content[config_name] = current_content

    def apply(self, config_name: str, force_copy: bool, compilation_map: Dict[str, InstallHandler], possible_config_hashes: Set[str], path_prefix: Optional[str] = None) -> None:
        for target in self.targets:
            self.__apply_single_target(
                target, config_name, force_copy, compilation_map, possible_config_hashes, path_prefix)

    def __apply_single_target(self, target: str, config_name: str, force_copy: bool, compilation_map: Dict[str, InstallHandler], possible_config_hashes: Set[str], path_prefix: Optional[str]) -> None:
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

        content_hash = utils.hash.sha256(content)

        target_hash: Optional[str] = None
        if os.path.isfile(target):
            target_hash = utils.hash.sha256_file(target)

        if content_hash == target_hash:
            dot_log_already_installed(content_hash, target)
            return

        if not os.path.isdir(os.path.dirname(target)):
            utils.path.makedirs(os.path.dirname(target))

        apply_command = DotApplyCommand(
            force_copy, content, needs_sudo, executable)
        apply_command.run(target, possible_config_hashes)

        if device_specific:
            dot_log_installed(content_hash, target, installed_once=True)
        else:
            dot_log_installed(content_hash, target, installed_once=False)

        if self.name in compilation_map:
            compilation_map[self.name].needsCompilation = True


class InvalidComputedDotLink(Exception):
    pass


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


COMPUTED_DOT_LINKS = __compute_dot_links()
