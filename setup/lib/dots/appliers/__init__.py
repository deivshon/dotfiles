from typing import Dict, List
from setup.lib.dots.names import DotsNames
from setup.lib.dots.appliers.gtk import GTK_APPLIER
from setup.lib.dots.appliers.waybar import WAYBAR_APPLIER
from setup.lib.dots.appliers.applier import Applier, DotApplier
from setup.lib.dots.appliers.vscode.theme import VSCODE_THEME_APPLIER
from setup.lib.dots.appliers.vscode.extensions import VSCODE_EXTENSIONS_APPLIER


APPLIERS: List[Applier] = [
    VSCODE_THEME_APPLIER,
    VSCODE_EXTENSIONS_APPLIER,
    GTK_APPLIER,
]

DOT_APPLIERS: Dict[str, DotApplier] = {
    DotsNames.WAYBAR_CONFIG: WAYBAR_APPLIER
}
