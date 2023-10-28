from typing import List
from setup.lib.dots.appliers.applier import Applier
from setup.lib.dots.appliers.vscode import VSCODE_APPLIER


APPLIERS: List[Applier] = [
    VSCODE_APPLIER
]