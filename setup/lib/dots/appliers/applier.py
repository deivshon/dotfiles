from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class Applier():
    name: str
    run: Callable[[Dict], None]
    apply_once: bool
    required: List[str]


@dataclass
class DotApplier():
    name: str
    run: Callable[[str], str]
