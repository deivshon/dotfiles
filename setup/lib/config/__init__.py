import json

from setup.lib import LIB_DIR
from setup.lib.dots import LINKS_FILE
from setup.lib.dots.dots import LINK_SUBS

SUBSTITUTIONS = "substitutions"
EXPANDED_SUBSTITUTIONS = "setup-expanded-substitutions"

MAIN_COLOR = "main-color"
SECONDARY_COLOR = "secondary-color"
PRESET = "preset"

with open(LINKS_FILE, "r") as file:
    links_list = json.loads(file.read())

EXPECTED_SUBSTITUTIONS = []
for link in links_list:
    if LINK_SUBS not in links_list[link]:
        continue

    for sub in links_list[link][LINK_SUBS]:
        if sub in EXPECTED_SUBSTITUTIONS:
            continue

        EXPECTED_SUBSTITUTIONS += [sub]

__CONFIGS_LIST_FILE = f"{LIB_DIR}/../data/configs.json"
with open(__CONFIGS_LIST_FILE) as f:
    AVAILABLE_CONFIGS = json.loads(f.read())
