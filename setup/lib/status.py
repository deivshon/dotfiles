import json

from typing import Optional
from dataclasses import dataclass

from setup.lib import LIB_DIR

SETUP_STATUS = f"{LIB_DIR}/../setup_status.json"
PACKAGES_INSTALLED = "packages-installed"
POST_INSTALL_OPS = "post-install-operations"
CONFIG = "config"


@dataclass
class SetupStatus():
    packages_installed: bool
    post_install_operations: bool
    config: Optional[str]

    def dumps(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def loads(cls, status_path: str):
        with open(status_path, "r") as file:
            data = json.loads(file.read())
        return cls(**data)
