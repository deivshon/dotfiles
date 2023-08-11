import re
import subprocess

from libqtile import bar, widget
from libqtile.config import Drag, Group, Key, Screen
from libqtile.lazy import lazy
from libqtile.layout.xmonad import MonadTall

mod = "mod4"
terminal = "st"

keys = [
    Key([mod, "shift"], "u", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),

    Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod], "v", lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window"),
    Key([mod], "Tab", lazy.layout.next(),
        desc="Move window focus to other window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod, "shift"], "Return", lazy.layout.swap_main()),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "d", lazy.spawn("rofi -show drun -display-drun"), desc="Launch rofi"),

    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
]

groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(
                    i.name),
            ),
        ]
    )

layouts = [
    MonadTall(
        border_focus="<sub<main-color>>",
        border_normal="<sub<secondary-color>>",
        border_width=2,
        new_client_position="top"
    ),
]

widget_defaults = dict(
    font="nimbu sans bold",
    fontsize=12,
    padding=3,
)

extension_defaults = widget_defaults.copy()

p = subprocess.run(["xrandr"], capture_output=True)
screen_count = 0
for line in p.stdout.decode().splitlines():
    if re.match(r".* connected.*", line):
        screen_count += 1

screens = []
for i in range(0, max(screen_count, 1)):
    screens.append(
        Screen(
            bottom=bar.Bar(
                [
                    widget.GroupBox(),
                    widget.Prompt(),
                    widget.WindowName(),
                    widget.Clock(format="%Y-%m-%d %a %I:%M %p"),
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
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

auto_minimize = True
wl_input_rules = None

wmname = "LG3D"
