import os
import json
import subprocess

from typing import Dict, List, Optional, Set

from setup.lib import log
from setup.lib.utils import HOME_DIR
from setup.lib.dots.appliers.applier import DotApplier

__MONITOR_PREFIXES: List[str] = [
    "DP-",
    "HDMI-A-",
    "HDMI-B-",
    "DVI-I-",
    "DVI-D-",
    "DVI-A-",
    "VGA-",
    "eDP-"
]
__INSTALLED_WAYBAR_CONFIG_FILE = os.path.join(
    HOME_DIR, ".config", "waybar", "config")
__HYPRLAND_WORKSPACES = "hyprland/workspaces"
__PERSISTENT = "persistent_workspaces"
__EMPTY_PERSISTENT_DATA: Dict[str, List[str]] = {
    "1": [],
    "2": [],
    "3": [],
    "4": [],
    "5": [],
    "6": [],
    "7": [],
    "8": [],
    "9": []
}


def __get_existing_monitors() -> Set[str]:
    existing_monitors: Set[str] = set()
    try:
        with open(__INSTALLED_WAYBAR_CONFIG_FILE) as f:
            waybar_config = json.loads(f.read())
        for workspace in __EMPTY_PERSISTENT_DATA:
            if workspace not in waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT]:
                continue

            existing_monitors = existing_monitors.union(
                set(waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace]))
    except Exception as _:
        return set()

    return existing_monitors


__EXISTING_MONITORS = __get_existing_monitors()


def __generate_names() -> Set[str]:
    names: Set[str] = set()
    for prefix in __MONITOR_PREFIXES:
        for n in range(0, 10):
            names.add(f"{prefix}{n}")

    return names


def __get_wlr_randr_monitors() -> Optional[Set[str]]:
    wlr_randr_monitors: Set[str] = set()
    try:
        wlr_randr_p = subprocess.run(["wlr-randr"], capture_output=True)
        if wlr_randr_p.returncode != 0:
            log.error(
                f"wlr-randr returned {log.RED}status code {wlr_randr_p.returncode}{log.NORMAL}, its output could not be analyzed")
        else:
            for line in wlr_randr_p.stdout.decode().splitlines():
                if line.startswith(" ") or line.startswith("\t"):
                    continue
                else:
                    split_line = line.split(" ")
                    if len(split_line) == 0:
                        continue

                    log.info(
                        f"Detected monitor name {log.YELLOW}{split_line[0]}")
                    wlr_randr_monitors.add(split_line[0])
    except Exception as e:
        log.error(f"Could not run wlr-randr output analysis: {log.RED}{e}")
        return None

    return wlr_randr_monitors


def __waybar_applier(waybar_config_str: str) -> str:
    monitor_names = __generate_names().union(__EXISTING_MONITORS)
    waybar_config = json.loads(waybar_config_str)

    if __HYPRLAND_WORKSPACES not in waybar_config:
        log.error(
            f"No `{__HYPRLAND_WORKSPACES}` key in waybar configuration file")
        return waybar_config_str

    if __PERSISTENT not in waybar_config[__HYPRLAND_WORKSPACES]:
        waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT] = __EMPTY_PERSISTENT_DATA
    for workspace in __EMPTY_PERSISTENT_DATA:
        if workspace not in waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT]:
            waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace] = []

    wlr_randr_monitors = __get_wlr_randr_monitors()
    if wlr_randr_monitors is not None:
        monitor_names = monitor_names.union(wlr_randr_monitors)

    for workspace in waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT]:
        for name in monitor_names:
            if name not in waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace]:
                waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace].append(
                    name)
        waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace] = sorted(
            waybar_config[__HYPRLAND_WORKSPACES][__PERSISTENT][workspace])

    return json.dumps(waybar_config, indent=4)


WAYBAR_APPLIER: DotApplier = DotApplier(
    name="waybar-persistent-workspaces", run=__waybar_applier)
