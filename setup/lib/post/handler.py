from typing import Dict
from abc import ABC, abstractmethod

from setup.lib import log
from setup.lib.config.config import get_lite_mode_bool


class PostOperationsHandler(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @staticmethod
    @abstractmethod
    def needed_in_lite() -> bool:
        ...

    @classmethod
    @abstractmethod
    def _trigger_impl(cls, config):
        ...

    @classmethod
    def trigger(cls, config: Dict):
        lite_mode = get_lite_mode_bool(config)
        if lite_mode and not cls.needed_in_lite():
            log.info(f"{cls.name()} {
                     log.CYAN}post operation skipped on lite mode{log.NORMAL}")
            return

        cls._trigger_impl(config)
        log.info(f"{cls.name()} {
                 log.GREEN}post operation completed{log.NORMAL}")
