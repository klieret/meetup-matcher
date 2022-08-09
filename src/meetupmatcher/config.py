from __future__ import annotations

from pathlib import Path, PurePath

from meetupmatcher.util.compat_resource import resources
from meetupmatcher.util.log import logger

_config_search_dirs = [
    Path("."),
    Path("~").expanduser(),
]
_config_search_filenames = [
    "meetupmatcher.yaml",
]


def get_default_config_path() -> Path:
    with resources.path("meetupmatcher.config_files", "default.yaml") as path:
        return path


def find_config(supplied_path: str | PurePath | None = None) -> Path:
    """Returns path to config file depending on user specified setting"""
    if supplied_path:
        supplied_path = Path(supplied_path)
        if supplied_path.is_file():
            return supplied_path
        else:
            raise FileNotFoundError(f"Supplied path {supplied_path} is not a file.")
    for dir in _config_search_dirs:
        for filename in _config_search_filenames:
            path = dir / filename
            if path.is_file():
                logger.info("Using config file %s from search dirs.", path)
                return path
    path = get_default_config_path()
    logger.warning(
        "Falling back to default config file %s. If this is not what you want,"
        " copy this file to your home directory or working directory and"
        "modify it.",
        path,
    )
    return path
