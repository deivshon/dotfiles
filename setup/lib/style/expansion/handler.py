from abc import ABC, abstractstaticmethod


class ExpansionHandler(ABC):
    @abstractstaticmethod
    def expand(color_data, expansion_data):
        ...
