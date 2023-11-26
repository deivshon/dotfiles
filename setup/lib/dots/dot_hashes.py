
from typing import Set

from setup.lib import utils
from setup.lib.dots.binary_link import BINARY_DOT_LINKS
from setup.lib.dots.computed_link import COMPUTED_DOT_LINKS


def __get_all_hashes() -> Set[str]:
    hashes = set()
    for computed_link in COMPUTED_DOT_LINKS:
        if isinstance(computed_link.content, str):
            hashes.add(utils.hash.sha256(computed_link.content))
        else:
            for config_name in computed_link.content:
                config_content = computed_link.content[config_name]
                hashes.add(utils.hash.sha256(config_content))

    for binary_link in BINARY_DOT_LINKS:
        hashes.add(utils.hash.sha256(binary_link.content))

    return hashes


DOTFILES_HASHES = __get_all_hashes()
