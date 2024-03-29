import os
import subprocess
import sys

from typing import Callable, List, Optional, Union, NoReturn

from libqtile import hook
from libqtile.lazy import lazy
from libqtile import bar, widget
from libqtile.layout.max import Max
from libqtile.core.manager import Qtile
from libqtile.layout.xmonad import MonadTall
from libqtile.layout.floating import Floating
from libqtile.config import Drag, Group, Key, Screen


sys.path.insert(1, os.path.dirname(__file__))
from config_device import primary_screen, workspace_bindings, screen_count, apps_to_start
from battery_graph import BatteryGraph

do_nothing = lambda *_: None


def getenv_or_die(name: str) -> Union[str, NoReturn]:
    var = os.getenv(name)
    if var is None:
        sys.exit(1)

    return var


def check_arch_updates():
    p = subprocess.run(["command-cache", "-p", "600000", "-d",
                       "/tmp/command-cache/aus/", "-c", "arch-updates-status -f %p/%y -p"], capture_output=True)

    if p.returncode == 0:
        return p.stdout.decode().strip()


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


@hook.subscribe.startup_once
def autostart():
    for app in apps_to_start:
        subprocess.Popen([app.binary] + app.args)


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
    Key([mod, "shift"], "Tab", lazy.layout.previous(),
        desc="Move window focus to previous window"),
    Key([mod, "control"], "Tab", lazy.next_screen(),
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
    Key([], "XF86AudioRaiseVolume", lazy.spawn(
        "pactl-ewr -c 5"), desc="Increase volume"),
    Key([], "XF86AudioLowerVolume", lazy.spawn(
        "pactl-ewr -c -5"), desc="Decrease volume"),
    Key([], "XF86AudioMute", lazy.spawn(
        "pactl-ewr -t"), desc="Toggle audio"),
    Key([mod], "p", lazy.spawn(
        "flameshot gui"), desc="Start screenshot area selection"),

    Key([mod], "f", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
]

workspaces = [Group(i) for i in "123456789"]


def switch_workspace(name: str) -> Callable:
    def _inner(qtile: Qtile) -> None:
        bound_screen = workspace_bindings[screen_count][name]

        qtile.focus_screen(bound_screen)
        qtile.groups_map[name].cmd_toscreen()

    return _inner


def move_window(group: str) -> Callable:
    def _inner(qtile: Qtile) -> None:
        current_window = qtile.current_window
        if current_window is None:
            return

        bound_screen = workspace_bindings[screen_count][group]

        current_window.togroup(group)
        qtile.focus_screen(bound_screen)
        qtile.groups_map[group].cmd_toscreen()

    return _inner


MAIN_COLOR = "<sub<main-color>>"
SECONDARY_COLOR = "<sub<secondary-color>>"

for w in workspaces:
    keys.append(Key([mod], w.name, lazy.function(
        switch_workspace(w.name)), desc=f"Switch to workspace {w.name}")
    )
    keys.append(Key([mod, 'shift'], w.name, lazy.function(
        move_window(w.name))))

layouts = [
    MonadTall(
        border_focus=MAIN_COLOR,
        border_normal=SECONDARY_COLOR,
        border_width=1,
        ratio=0.55,
        new_client_position="top"
    ),
    Max(
        border_focus=MAIN_COLOR,
        border_normal=SECONDARY_COLOR,
        border_width=1
    ),
]


widget_defaults = dict(
    font="Jet Brains Mono NF SemiBold",
    fontsize=12,
    padding=3,
)

extension_defaults = widget_defaults.copy()

widget.GroupBox.button_press = do_nothing

screens = []
for i in range(0, screen_count):
    screens.append(
        Screen(
            bottom=bar.Bar(
                [
                    widget.CurrentLayoutIcon(custom_icon_paths=[os.path.expanduser("~/.icons/qtile/")],
                                             scale=1.3,
                                             padding=0),
                    widget.GroupBox(
                        this_screen_border=SECONDARY_COLOR,
                        this_current_screen_border=MAIN_COLOR,
                        other_current_screen_border="#000000",
                        other_screen_border="#000000",
                        borderwidth=2,
                        highlight_method="line",
                        padding=3,
                        fontsize=12
                    ),
                    widget.Prompt(),
                    widget.WindowName(),
                    widget.Spacer(length=7),
                    widget.TextBox("DISK ", padding=4),
                    widget.HDDGraph(
                        border_color=MAIN_COLOR,
                        graph_color=MAIN_COLOR,
                        fill_color=MAIN_COLOR,
                        border_width=1
                    ),
                    widget.TextBox("CPU 󰒋", padding=2),
                    widget.CPUGraph(
                        border_color=MAIN_COLOR,
                        graph_color=MAIN_COLOR,
                        fill_color=MAIN_COLOR,
                        border_width=1
                    ),
                    widget.TextBox("RAM ", padding=0),
                    widget.MemoryGraph(
                        border_color=MAIN_COLOR,
                        graph_color=MAIN_COLOR,
                        fill_color=MAIN_COLOR,
                        border_width=1
                    ),
                    widget.TextBox(
                        "BAT ", padding=0) if battery_path is not None else widget.Spacer(length=0),
                    BatteryGraph(
                        battery_path=battery_path,
                        border_color=MAIN_COLOR,
                        graph_color=MAIN_COLOR,
                        fill_color=MAIN_COLOR,
                        border_width=1,
                        frequency=30,
                        samples=120
                    ) if battery_path is not None else widget.Spacer(length=0),
                    widget.Clock(format="%Y-%m-%d %H:%M:%S"),
                    widget.Systray() if (i + 1) == primary_screen else widget.Spacer(length=0),
                    widget.GenPollText(func=check_arch_updates,
                                       update_interval=1,
                                       fmt=" {}"),
                ],
                20,
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
    border_focus=MAIN_COLOR,
    border_normal=SECONDARY_COLOR,
)
