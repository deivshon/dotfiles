import os
import time

from typing import Set
from dataclasses import dataclass

from setup.lib import utils


@dataclass
class DotApplyCommand:
    force_copy: bool
    content: str | bytes
    needs_sudo: bool
    executable: bool

    def run(self, target: str, possible_config_hashes: Set[str]):
        if os.path.isfile(target) and utils.hash.sha256_file(target) not in possible_config_hashes:
            backup_target = os.path.join(os.path.dirname(
                target), f"{time.time_ns()}_{os.path.basename(target)}.bkp")

            utils.path.copy(target, backup_target, force=True,
                            needs_sudo=self.needs_sudo)
            utils.path.make_non_executable(backup_target, sudo=self.needs_sudo)

        utils.path.write_to_file(self.content, target, force=self.force_copy,
                                 needs_sudo=self.needs_sudo)
        if self.executable:
            utils.path.make_executable(target, sudo=self.needs_sudo)
