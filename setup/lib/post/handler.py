from typing import Dict
from abc import ABC, abstractmethod

from setup.lib import log


class PostOperationsHandler(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @classmethod
    @abstractmethod
    def _trigger_impl(cls, config):
        ...

    @classmethod
    def trigger(cls, config: Dict):
        cls._trigger_impl(config)
        log.info(f"{cls.name()} post operation completed")
