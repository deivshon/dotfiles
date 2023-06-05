from typing import List

from abc import ABC, abstractmethod


class VariableTargetHandler(ABC):
    @staticmethod
    @abstractmethod
    def get_targets() -> List:
        ...
