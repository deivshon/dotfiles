import json

from setup.lib.configs import LINKS_FILE
from setup.lib.configs.configs import SUBS

SUBSTITUTIONS = "substitutions"
EXPANDED_SUBSTITUTIONS = "setup-expanded-substitutions"

MAIN_COLOR = "mainColor"
SECONDARY_COLOR = "secondaryColor"

with open(LINKS_FILE, "r") as f:
    links_list = json.loads(f.read())

EXPECTED_SUBSTITUTIONS = []
for link in links_list:
    if SUBS not in links_list[link]:
        continue

    for sub in links_list[link][SUBS]:
        if sub in EXPECTED_SUBSTITUTIONS:
            continue

        EXPECTED_SUBSTITUTIONS += [sub]
