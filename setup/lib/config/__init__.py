import json
from typing import Dict

from setup.lib import LIB_DIR
from setup.lib.const.config import PRESET
from setup.lib.config.config import apply_defaults, apply_preset, check, expand, initialize


__CONFIGS_LIST_FILE = f"{LIB_DIR}/../data/configs.json"
with open(__CONFIGS_LIST_FILE) as f:
    AVAILABLE_CONFIGS = json.loads(f.read())

CONFIGS: Dict[str, Dict] = {}
for config_name in AVAILABLE_CONFIGS:
    selected_config = AVAILABLE_CONFIGS[config_name]
    initialize(selected_config)

    if PRESET in selected_config:
        apply_preset(
            selected_config, selected_config[PRESET])

    # Set lite mode do whatever value since files with
    # non theme substitutions can't use the backup features
    # anyway
    apply_defaults(selected_config, lite_mode=True)
    expand(selected_config)
    check(selected_config)
    CONFIGS[config_name] = selected_config
