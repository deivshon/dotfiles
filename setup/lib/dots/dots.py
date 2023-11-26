from typing import Dict, Optional

from setup.lib import log
from setup.lib.dots.appliers import APPLIERS
from setup.lib.install.handler import InstallHandler
from setup.lib.dots.dot_hashes import DOTFILES_HASHES
from setup.lib.const.config import CONFIG_SUBSTITUTIONS
from setup.lib.dots.binary_link import BINARY_DOT_LINKS
from setup.lib.dots.computed_link import COMPUTED_DOT_LINKS


def link(config, config_name: str, force_copy=False, compilation_map: Dict[str, InstallHandler] = {}, path_prefix: Optional[str] = None, run_appliers: bool = True):
    for computed_link in COMPUTED_DOT_LINKS:
        computed_link.apply(config_name, force_copy,
                            compilation_map, DOTFILES_HASHES, path_prefix)

    for binary_link in BINARY_DOT_LINKS:
        binary_link.apply(force_copy, DOTFILES_HASHES, path_prefix)

    print("\n", end="")

    if run_appliers:
        for applier in APPLIERS:
            log.info(f"Running applier {log.GREEN}{applier.name}")
            applier.run(config[CONFIG_SUBSTITUTIONS])

    print("\n", end="")
