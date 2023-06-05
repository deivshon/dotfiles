from abc import ABC, abstractmethod


class ExpansionHandler(ABC):
    @staticmethod
    @abstractmethod
    def expand(color_data, expansion_data):
        ...
