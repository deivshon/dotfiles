import os
import re
import sys
import subprocess

from typing import Callable

from libqtile.lazy import lazy
from libqtile import bar, widget
from libqtile.layout.max import Max
from libqtile.core.manager import Qtile
from libqtile.layout.xmonad import MonadTall
from libqtile.layout.floating import Floating
from libqtile.config import Drag, Group, Key, Screen


sys.path.insert(1, os.path.dirname(__file__))
import config_device

mod = "mod4"
terminal = "alacritty"

keys = [
    Key([mod, "shift"], "u", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod, "shift"], "r", lazy.reload_config(), desc="Reload the config"),

    Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "v", lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window"),
    Key([mod], "Tab", lazy.layout.next(),
        desc="Move window focus to other window"),
    Key(
        [mod],
        "x",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod, "shift"], "Return", lazy.layout.swap_main()),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "d", lazy.spawn(
        "rofi -show drun -display-drun ''"), desc="Launch rofi"),
    Key([mod], "l", lazy.spawn("xlock"), desc="Lock screen"),

    Key([mod], "f", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
]

workspaces = [Group(i) for i in "123456789"]


def switch_workspace(name: str) -> Callable:
    def _inner(qtile: Qtile) -> None:
        if len(qtile.screens) == 1:
            qtile.groups_map[name].cmd_toscreen()
            return

        if name in "13579":
            qtile.focus_screen(0)
        else:
            qtile.focus_screen(1)

        qtile.groups_map[name].cmd_toscreen()

    return _inner


for i in workspaces:
    keys.append(Key([mod], i.name, lazy.function(
        switch_workspace(i.name)), desc=f"Switch to workspace {i.name}")
    )
    keys.append(Key([mod, 'shift'], i.name, lazy.window.togroup(i.name)))

layouts = [
    MonadTall(
        border_focus="<sub<main-color>>",
        border_normal="<sub<secondary-color>>",
        border_width=1,
        new_client_position="top"
    ),
    Max(),
]


widget_defaults = dict(
    font="nimbu sans bold",
    fontsize=12,
    padding=3,
)

extension_defaults = widget_defaults.copy()

p = subprocess.run(["xrandr"], capture_output=True)
screen_count = 1
if p.returncode == 0:
    screen_count = 0
    for line in p.stdout.decode().splitlines():
        if re.match(r".* connected.*", line):
            screen_count += 1

screens = []
for i in range(0, screen_count):
    screens.append(
        Screen(
            bottom=bar.Bar(
                [
                    widget.GroupBox(
                        this_screen_border="<sub<secondary-color>>",
                        this_current_screen_border="<sub<main-color>>",
                        other_current_screen_border="#000000",
                        other_screen_border="#000000",
                        borderwidth=2,
                        highlight_method="line"
                    ),
                    widget.Prompt(),
                    widget.WindowName(),
                    widget.TextBox("CPU "),
                    widget.CPUGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>.3",
                        border_width=1
                    ),
                    widget.TextBox("DISK "),
                    widget.HDDGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>.3",
                        border_width=1
                    ),
                    widget.TextBox("RAM "),
                    widget.MemoryGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>.3",
                        border_width=1
                    ),
                    widget.Clock(format="%Y-%m-%d %H:%M:%S"),
                    widget.BatteryIcon(),
                    widget.Systray() if i == config_device.primary_screen else widget.Spacer(length=0),
                ],
                24,
            ),
            wallpaper="<sub<qtile-wallpaper-path>>",
            wallpaper_mode="fill"
        ),
    )


mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
]

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = True
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

auto_minimize = True
wl_input_rules = None

wmname = "LG3D"

floating_layout = Floating(
    border_width=1,
    border_focus="<sub<main-color>>",
    border_normal="<sub<secondary-color>>",
)
