# -*- coding: utf-8 -*-
"""Core functionality for chonf's xml configuration parser.

Functions:

    read(keys: List[str], dir_path: pathlib.Path, *args, **kargs) -> Any:
        Tries to read a configuration option from a xml file.

"""
from functools import cache
from pathlib import Path
from typing import Any, List, Set

import xmltodict

from chonf.exceptions import FileAccessError, NotSubtree, SkipSource


def read(keys: List[str], path: Path, *_, **__) -> Any:
    """Read configuration option from a yaml file.

    Args:
        keys (List[str]): Ordered keys to access the option.
        dir_path (pathlib.Path): Path to the toml file

    Returns:
        Any: Whatever data is found in the file with the given keys.
    """
    config = load_configs(path / "config.xml")
    try:
        for key in keys:
            config = config[key]
    except KeyError as err:
        raise SkipSource from err
    return config


def list_children(keys: List[str], path: Path, *_, **__) -> Set[str]:
    """List all children of a configuration node on a yaml file.

    Args:
        keys (List[str]): Ordered keys to access the node.
        dir_path: (pathlib.Path): path object representing the file

    Returns:
        Set[str]: list of children keys to requested node, might be empty.

    """
    config = load_configs(path / "config.xml")
    try:
        for key in keys:
            config = config[key]
    except KeyError:
        return set()
    if config is None:
        return set()
    if isinstance(config, dict):
        return set(config.keys())
    raise NotSubtree(config)


@cache
def load_configs(path: Path) -> dict:
    """Read yaml file into a dict.

    This wraps the safe_load() function from the yaml package,
    and will use it's default behaviour when called with
    only a file path.

    Args:
        path (pathlib.Path): Path to the yaml file.

    Returns:
        dict: Data read from yaml file.
    """
    try:
        configs = xmltodict.parse(path.read_text())
        if configs is None:
            return {}
        if isinstance(configs, dict):
            return configs["configs"]
        raise
    except FileNotFoundError:
        return {}
    except Exception as err:
        raise FileAccessError from err
