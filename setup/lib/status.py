import json

from typing import Optional
from dataclasses import dataclass

from setup.lib import LIB_DIR

SETUP_STATUS = f"{LIB_DIR}/../setup_status.json"
PACKAGES_INSTALLED = "packages-installed"
POST_INSTALL_OPS = "post-install-operations"
STYLE = "style"


@dataclass
class SetupStatus():
    packages_installed: bool
    post_install_operations: bool
    style: Optional[str]

    def dumps(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def loads(cls, file: str):
        with open(file, "r") as f:
            data = json.loads(f.read())
        print(data)
        return cls(**data)
