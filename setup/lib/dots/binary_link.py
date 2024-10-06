import json
import os

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from setup.lib import log, utils
from setup.lib.config.config import get_lite_mode_bool
from setup.lib.dots.appliers import DOT_APPLIERS
from setup.lib.dots.apply_command import DotApplyCommand
from setup.lib.dots.dot_link import DotLink, InvalidDotLink
from setup.lib.dots import DOTFILES_DIR, BINARY_DOT_LINKS_FILE
from setup.lib.dots.dots_log import dot_log_already_installed, dot_log_installed, dot_log_skipping_because_lite

from setup.lib.dots.flags import SUDO_FLAG
from setup.lib.dots.names import BinaryDotsNames


@dataclass
class BinaryDotLink():
    name: str
    target: str
    flags: List[str]
    content: bytes
    needed_in_lite: bool

    def __init__(self, dot_link: DotLink):
        if dot_link.target is None:
            raise InvalidDotLink

        self.needed_in_lite = dot_link.needed_in_lite
        self.target = os.path.abspath(
            dot_link.target.replace("~", utils.HOME_DIR))
        self.name = dot_link.name
        self.flags = dot_link.flags

        source = f"{DOTFILES_DIR}/{dot_link.source}"
        if not os.path.isfile(source):
            raise InvalidDotLink
        with open(source, "rb") as f:
            self.content = f.read()

    def apply(self, config: Dict, force_copy: bool, possible_config_hashes: Set[str], path_prefix: Optional[str] = None):
        target = self.target
        if path_prefix is not None:
            target = f"{path_prefix}{target}"

        config_lite_mode = get_lite_mode_bool(config)
        needs_apply_on_mode = self.needed_in_lite or (not config_lite_mode)

        needs_sudo = SUDO_FLAG in self.flags
        content_hash = utils.hash.sha256(self.content)
        target_hash = None
        if os.path.isfile(target):
            target_hash = utils.hash.sha256_file(target)

        if not needs_apply_on_mode:
            dot_log_skipping_because_lite(
                content_hash, target, has_non_theme_subs=False)
            return

        if content_hash == target_hash:
            dot_log_already_installed(
                content_hash, target, has_non_theme_subs=False)
            return

        target_dir = os.path.dirname(target)
        if not os.path.isdir(target_dir):
            utils.path.makedirs(target_dir)
        apply_command = DotApplyCommand(
            force_copy=force_copy,
            content=self.content,
            has_non_theme_subs=False,
            needs_sudo=needs_sudo,
            executable=False
        )
        apply_command.run(target, possible_config_hashes)

        dot_log_installed(content_hash, target,
                          installed_once=False, has_non_theme_subs=False)


def __binary_dot_links() -> List[BinaryDotLink]:
    binary_links: List[BinaryDotLink] = []
    with open(BINARY_DOT_LINKS_FILE, "r") as file:
        __binary_links_dict = json.loads(file.read())
        for key in __binary_links_dict:
            if key not in BinaryDotsNames.__dict__.values():
                log.failure(
                    f"Naming inconsistency: \"{key}\" does not appear in allowed names")

            if key in DOT_APPLIERS:
                log.failure(
                    "Binary dot links can't have a related dot applier")

            dot_link = DotLink(
                name=key, **__binary_links_dict[key], dot_applier=None)
            binary_links.append(BinaryDotLink(dot_link))
    return binary_links


BINARY_DOT_LINKS = __binary_dot_links()
