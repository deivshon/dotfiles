import os
import time

from typing import Optional, Set
from dataclasses import dataclass

from setup.lib import utils


@dataclass
class DotApplyCommand:
    force_copy: bool
    content: str | bytes
    has_non_theme_subs: bool
    needs_sudo: bool
    executable: bool

    def run(self, target: str, possible_config_hashes: Set[str]):
        old_content: Optional[bytes] = None
        if os.path.isfile(target):
            with open(target, "rb") as f:
                old_content = f.read()

        applied: bool = False
        try:
            applied = utils.path.write_to_file(self.content, target, force=self.force_copy,
                                               needs_sudo=self.needs_sudo)
            if self.executable:
                utils.path.make_executable(target, sudo=self.needs_sudo)
        finally:
            if not applied or old_content is None or self.has_non_theme_subs:
                return

            if utils.hash.sha256(old_content) not in possible_config_hashes:
                backup_target = os.path.join(os.path.dirname(
                    target), f"{os.path.basename(target)}.{time.time_ns()}.bak")

                utils.path.write_to_file(
                    old_content, backup_target, force=True, needs_sudo=self.needs_sudo)
                utils.path.make_non_executable(
                    backup_target, sudo=self.needs_sudo)
