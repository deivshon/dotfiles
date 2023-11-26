from typing import Optional, Dict, List
from dataclasses import dataclass, field

from setup.lib.dots.appliers.applier import DotApplier


@dataclass
class _DotLink():
    name: str
    source: str
    target: Optional[str] = None
    subs: Dict[str, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    dot_applier: Optional[DotApplier] = None


class InvalidDotLink(Exception):
    pass
