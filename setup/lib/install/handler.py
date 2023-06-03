from abc import ABC, abstractmethod

from setup.lib import log


class InstallHandler(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @classmethod
    @abstractmethod
    def _compile_impl(cls):
        ...

    @classmethod
    def compile(cls):
        log.info(f"Starting {cls.name()} compilation")
        cls._compile_impl()
        log.info(f"Ended {cls.name()} compilation\n")

    @classmethod
    @abstractmethod
    def _download_impl(cls):
        ...

    @classmethod
    def download(cls):
        log.info(f"Starting {cls.name()} download")
        cls._download_impl()
        log.info(f"Ended {cls.name()} download\n")

    @classmethod
    def install(cls):
        cls.download()
        cls.compile()
