from abc import ABC, abstractmethod

from setup.lib import log


class InstallHandler(ABC):
    needsCompilation: bool = True

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @abstractmethod
    def _compile_impl(self):
        ...

    def compile(self):
        if not self.needsCompilation:
            log.info(
                f"{log.WHITE}Not compiling {self.name()} due to no changes")
            return

        log.info(f"{log.WHITE}Starting {self.name()} compilation")
        self._compile_impl()
        log.info(f"{log.WHITE}Ended {self.name()} compilation\n")

    @abstractmethod
    def _download_impl(self, pull: bool):
        ...

    def download(self, pull: bool = False):
        log.info(f"{log.WHITE}Starting {self.name()} download")
        self._download_impl(pull)
        log.info(f"{log.WHITE}Ended {self.name()} download\n")

    def install(self, pull: bool = False):
        self.download(pull)
        self.compile()
