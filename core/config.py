from pathlib import Path
from utils import Config

cf = Config(Path("./config.ini").resolve())


def get_config(section: str, option: str, raw=True) -> str:
    return cf.get(section, option, raw=raw)


def get_items(section: str, raw=True):
    return cf.items(section, raw=raw)


def getboolean_config(section: str, option: str, raw=True) -> bool:
    return cf.getboolean(section, option, raw=raw)


def items_config(section: str, raw=True):
    return cf.items(section, raw=raw)
