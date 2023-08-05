# -*- coding: utf-8 -*-
"""Core functionality for chonf's python configuration parser.

Functions:

    read(keys: List[str], dir_path: pathlib.Path, *args, **kargs) -> Any:
        Tries to read a configuration option from a json file.

"""
from importlib.util import spec_from_file_location, module_from_spec
from functools import cache
from pathlib import Path
from typing import Any, List, Set

from chonf.exceptions import FileAccessError, NotSubtree, SkipSource


def read(keys: List[str], path: Path, *_, **__) -> Any:
    """Read configuration option from a Python file.

    Args:
        keys (List[str]): Ordered keys to access the option.
        dir_path: (pathlib.Path): path object representing the file

    Returns:
        Any: Whatever data is found in the file with the given keys.
    """
    config = load_configs(path / "config.py")
    try:
        for key in keys:
            config = config[key]
    except KeyError as err:
        raise SkipSource from err
    return config


def list_children(keys: List[str], path: Path, *_, **__) -> Set[str]:
    """List all children of a configuration node from a python script.

    Args:
        keys (List[str]): Ordered keys to access the node.
        dir_path: (pathlib.Path): path object representing the file

    Returns:
        Set[str]: list of children keys to requested node, might be empty.

    """
    config = load_configs(path / "config.py")
    try:
        for key in keys:
            config = config[key]
    except KeyError:
        return set()
    if isinstance(config, dict):
        return set(config.keys())
    raise NotSubtree(config)


@cache
def load_configs(path: Path) -> dict:
    """Read configurations from python script into dict.

    The script should contain a "configs" callable to
    receive no args and return a dictionary of configs,
    or a dictionary itself to be directly passed as configuration.

    Args:
        path (pathlib.Path): Path to the python file.

    Returns:
        dict: Configs gathered from python script.
    """
    try:
        spec = spec_from_file_location("userchonf", path)
        if spec is None:
            return {}
        script = module_from_spec(spec)
        loader = spec.loader
        if loader is None:
            return {}
        loader.exec_module(script)
        if not hasattr(script, "configs"):
            return {}
        configs = script.configs
        if isinstance(configs, dict):
            return configs
        if callable(configs):
            return configs()
        return {}
    except FileNotFoundError:
        return {}
    except Exception as err:
        raise FileAccessError from err
