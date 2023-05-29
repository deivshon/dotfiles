from setup.lib import printing


def warning(msg: str):
    printing.colorPrint(f"Warning: {msg}", printing.YELLOW)


def info(msg: str):
    printing.colorPrint(f"{msg}", printing.WHITE)


def error(msg: str):
    printing.colorPrint(f"Error: {msg}", printing.RED)
