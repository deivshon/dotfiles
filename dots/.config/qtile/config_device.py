from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Application():
    binary: str
    args: List[str] = field(default_factory=list)


screen_count = 1
primary_screen = 1

apps_to_start: List[Application] = []

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
