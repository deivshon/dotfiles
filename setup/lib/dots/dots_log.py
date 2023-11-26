from setup.lib import log


def dot_log_already_installed(hash_digest: str, target: str) -> None:
    log.info(
        f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.RED}already installed{log.NORMAL} {log.YELLOW}{target}{log.NORMAL}")


def dot_log_installed(hash_digest: str, target: str, installed_once: bool) -> None:
    if installed_once:
        log.info(
            f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.GREEN}only ever install{log.NORMAL} {log.YELLOW}{target}")
    else:
        log.info(
            f"{log.BLUE}{hash_digest[0:4]}...{hash_digest[-4:]}{log.NORMAL} | {log.GREEN}installed in path{log.NORMAL} {log.YELLOW}{target}")
