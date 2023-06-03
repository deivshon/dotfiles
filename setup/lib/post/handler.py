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
    def _trigger_impl(cls, color_style):
        ...

    @classmethod
    def trigger(cls, color_style: Dict):
        cls._trigger_impl(color_style)
        log.info(f"{cls.name()} post operation completed")
