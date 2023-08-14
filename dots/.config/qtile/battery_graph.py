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

        val = self._getvalues()
        battery_level = val["level"]
        self.fulfill(battery_level)

    def _getvalues(self):
        val = {}

        try:
            with open(f"{self.battery_path}/capacity") as f:
                val["level"] = int(f.read().strip())
        except Exception:
            val["level"] = 0

        return val

    def update_graph(self):
        val = self._getvalues()

        self.push(val)
