import os
import re
import sys
import subprocess

from typing import Callable, Optional, Union, NoReturn

from libqtile.lazy import lazy
from libqtile import bar, widget
from libqtile.layout.max import Max
from libqtile.core.manager import Qtile
from libqtile.layout.xmonad import MonadTall
from libqtile.layout.floating import Floating
from libqtile.config import Drag, Group, Key, Screen


sys.path.insert(1, os.path.dirname(__file__))
from config_device import primary_screen, workspace_bindings
from battery_graph import BatteryGraph

do_nothing = lambda *_: None

def getenv_or_die(name: str) -> Union[str, NoReturn]:
    var = os.getenv(name)
    if var is None:
        sys.exit(1)

    return var

WIDGETS_CACHE_DIR = getenv_or_die("QTILE_WIDGETS_CACHE_DIR")
UPDATES_CACHE_FILE = f"{WIDGETS_CACHE_DIR}/{getenv_or_die('QTILE_UPDATES_CACHE_FILE')}"

def check_arch_updates():
    if not os.path.exists(UPDATES_CACHE_FILE):
        return "0"

    with open(UPDATES_CACHE_FILE) as f:
        return f.read().strip()


def read_file(path: str) -> Optional[str]:
    if not os.path.isfile(path):
        return None

    with open(path) as f:
        content = f.read()

    return content


def get_battery_path() -> Optional[str]:
    batteries_path = "/sys/class/power_supply"
    if not os.path.isdir(batteries_path):
        return None

    for dev in os.listdir(batteries_path):
        content = read_file(f"{batteries_path}/{dev}/type")

        if content is None:
            continue

        if content.strip() == "Battery":
            return f"{batteries_path}/{dev}"

    return None

battery_path = get_battery_path()
del get_battery_path
del read_file

mod = "mod4"
terminal = "alacritty"

keys = [
    Key([mod, "shift"], "u", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod, "shift"], "r", lazy.reload_config(), desc="Reload the config"),

    Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "v", lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window"),
    Key([mod], "Tab", lazy.layout.next(),
        desc="Move window focus to next window"),
    Key(["shift"], "Tab", lazy.layout.previous(),
        desc="Move window focus to previous window"),
    Key([mod, "shift"], "Tab", lazy.next_screen(),
        desc="Move focus to next monitor"),
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
    Key([], "XF86AudioRaiseVolume", lazy.spawn("change-vol-pactl +5%"), desc="Increase volume"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("change-vol-pactl -5%"), desc="Decrease volume"),
    Key([], "XF86AudioMute", lazy.spawn("change-vol-pactl toggle"), desc="Toggle"),

    Key([mod], "f", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
]

workspaces = [Group(i) for i in "123456789"]

def switch_workspace(name: str) -> Callable:
    def _inner(qtile: Qtile) -> None:
        bound_screen = workspace_bindings[len(qtile.screens)][name]

        qtile.focus_screen(bound_screen)
        qtile.groups_map[name].cmd_toscreen()

    return _inner


def move_window(group: str) -> Callable:
    def _inner(qtile: Qtile) -> None:
        current_window = qtile.current_window
        if current_window is None:
            return

        bound_screen = workspace_bindings[len(qtile.screens)][group]

        current_window.togroup(group)
        qtile.focus_screen(bound_screen)
        qtile.groups_map[group].cmd_toscreen()

    return _inner


for w in workspaces:
    keys.append(Key([mod], w.name, lazy.function(
        switch_workspace(w.name)), desc=f"Switch to workspace {w.name}")
    )
    keys.append(Key([mod, 'shift'], w.name, lazy.function(
        move_window(w.name))))

layouts=[
    MonadTall(
        border_focus="<sub<main-color>>",
        border_normal="<sub<secondary-color>>",
        border_width=1,
        ratio=0.55,
        new_client_position="top"
    ),
    Max(
        border_focus="<sub<main-color>>",
        border_normal="<sub<secondary-color>>",
        border_width=1
    ),
]


widget_defaults=dict(
    font="nimbu sans bold",
    fontsize=13,
    padding=3,
)

extension_defaults=widget_defaults.copy()

p=subprocess.run(["xrandr"], capture_output=True)
screen_count=1
if p.returncode == 0:
    screen_count=0
    for line in p.stdout.decode().splitlines():
        if re.match(r".* connected.*", line):
            screen_count += 1

widget.GroupBox.button_press = do_nothing

screens=[]
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
                    widget.Spacer(length=7),
                    widget.TextBox("DISK "),
                    widget.HDDGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>",
                        border_width=1
                    ),
                    widget.TextBox("CPU "),
                    widget.CPUGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>",
                        border_width=1
                    ),
                    widget.TextBox("RAM "),
                    widget.MemoryGraph(
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>",
                        border_width=1
                    ),
                    widget.TextBox("BAT "),
                    BatteryGraph(
                        battery_path=battery_path,
                        border_color="<sub<main-color>>",
                        graph_color="<sub<main-color>>",
                        fill_color="<sub<main-color>>",
                        border_width=1,
                        update_interval=60,
                        samples=120
                    ) if battery_path is not None else widget.Spacer(length=0),
                    widget.Clock(format="%Y-%m-%d %H:%M:%S"),
                    widget.Systray() if i == primary_screen else widget.Spacer(length=0),
                    widget.GenPollText(func=check_arch_updates,
                        update_interval=1,
                        fmt=" {}"),
                ],
                24,
            ),
            wallpaper="<sub<qtile-wallpaper-path>>",
            wallpaper_mode="fill"
        ),
    )


mouse=[
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
]

dgroups_key_binder=None
dgroups_app_rules=[]
follow_mouse_focus=True
bring_front_click=False
floats_kept_above=True
cursor_warp=True
auto_fullscreen=True
focus_on_window_activation="smart"
reconfigure_screens=True

auto_minimize=True
wl_input_rules=None

wmname="LG3D"

floating_layout=Floating(
    border_width=1,
    border_focus="<sub<main-color>>",
    border_normal="<sub<secondary-color>>",
)
