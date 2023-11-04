from typing import Dict, List
from setup.lib.dots.appliers.applier import Applier, DotApplier
from setup.lib.dots.appliers.gtk import GTK_APPLIER
from setup.lib.dots.appliers.vscode import VSCODE_APPLIER
from setup.lib.dots.appliers.waybar import WAYBAR_APPLIER
from setup.lib.dots.names import DotsNames


APPLIERS: List[Applier] = [
    VSCODE_APPLIER,
    GTK_APPLIER,
]

DOT_APPLIERS: Dict[str, DotApplier] = {
    DotsNames.WAYBAR_CONFIG: WAYBAR_APPLIER
}
