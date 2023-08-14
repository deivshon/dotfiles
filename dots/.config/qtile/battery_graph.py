from libqtile.widget import base
from libqtile.widget.graph import _Graph


class BatteryGraph(_Graph):
    """Display a battery level graph"""

    orientations = base.ORIENTATION_HORIZONTAL
    fixed_upper_bound = True

    def __init__(self, battery_path: str, **config):
        _Graph.__init__(self, **config)
        self.battery_path = battery_path
        self.maxvalue = 100

        battery_charge = self._getvalues()
        self.fulfill(battery_charge)

    def _getvalues(self):
        try:
            with open(f"{self.battery_path}/capacity") as f:
                level = int(f.read().strip())
        except Exception:
            level = 0

        return level

    def update_graph(self):
        self.push(self._getvalues())
