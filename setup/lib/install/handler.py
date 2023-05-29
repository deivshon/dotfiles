from abc import ABC, abstractmethod

from setup.lib import log


class InstallHandler(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @classmethod
    @abstractmethod
    def compile(cls):
        ...

    @classmethod
    @abstractmethod
    def download(cls):
        ...

    @classmethod
    def install(cls):
        cls.download()
        cls.compile()
