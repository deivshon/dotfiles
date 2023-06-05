import os
import venv
import subprocess

from typing import List

from setup.lib import log
from setup.lib import LIB_DIR
from setup.lib.venv import VENV_PATH

__VENV_REQUIREMENTS = os.path.abspath(f"{LIB_DIR}/../../requirements.txt")
__VENV_ENV_VAR = "dotfiles-venv"


def create():
    venv.create(VENV_PATH, with_pip=True)


def install_requirements():
    subprocess.run(
        [f"{VENV_PATH}/bin/pip", "install", "-r", __VENV_REQUIREMENTS], capture_output=True)


def run_with(script: str, args: List[str]) -> int:
    if not os.path.isdir(VENV_PATH):
        log.warning(f"Venv not detected, creating one at {VENV_PATH}\n")
        create()
        install_requirements()

    script_run = subprocess.run(
        [f"{VENV_PATH}/bin/python", script] + args,
        env=dict({"VIRTUAL_ENV": __VENV_ENV_VAR}, **os.environ.copy()))

    return script_run.returncode
