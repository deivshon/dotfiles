import json

from setup.lib.dots import LINKS_FILE
from setup.lib.dots.dots import SUBS

SUBSTITUTIONS = "substitutions"
EXPANDED_SUBSTITUTIONS = "setup-expanded-substitutions"

MAIN_COLOR = "main-color"
SECONDARY_COLOR = "secondary-color"

with open(LINKS_FILE, "r") as file:
    links_list = json.loads(file.read())

EXPECTED_SUBSTITUTIONS = []
for link in links_list:
    if SUBS not in links_list[link]:
        continue

    for sub in links_list[link][SUBS]:
        if sub in EXPECTED_SUBSTITUTIONS:
            continue

        EXPECTED_SUBSTITUTIONS += [sub]
