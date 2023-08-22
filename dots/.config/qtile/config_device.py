from typing import Dict, Dict

primary_screen = 0

workspace_bindings: Dict[int, Dict[str, int]] = {
    1: {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0
    },
    2: {
        "1": 0,
        "2": 1,
        "3": 0,
        "4": 1,
        "5": 0,
        "6": 1,
        "7": 0,
        "8": 1,
        "9": 0
    },
    3: {
        "1": 0,
        "2": 1,
        "3": 2,
        "4": 0,
        "5": 1,
        "6": 2,
        "7": 0,
        "8": 1,
        "9": 2
    }
}