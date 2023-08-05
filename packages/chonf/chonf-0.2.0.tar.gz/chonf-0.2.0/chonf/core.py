# -*- coding: utf-8 -*-
"""Provides core functionality for chonf.

Functions
---------
    * load - returns a dictionary constructed based on the provided
        model of configurations with data read from several sources.

Classes
-------
    * Option - to be used to create model dictionary to be passed on
        to the load function.

"""
from dataclasses import dataclass
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Union

from chonf.exceptions import (
    ConfigLoadingIncomplete,
    ConfigNotFound,
    ConfigReadingError,
    InvalidOption,
    NotSubtree,
    SkipSource,
)
from chonf.parsers import default_parsers
from chonf.paths import default_path


@dataclass
class BaseOption:
    """Base class for chonf options."""


@dataclass
class Option(BaseOption):
    """Dataclass to represent a config value to be read."""

    default: Any = None
    preprocess: Optional[Callable[[Any], Any]] = None


@dataclass
class Required(BaseOption):
    """Class to represent a required config value to be read."""

    preprocess: Optional[Callable[[Any], Any]] = None


@dataclass
class Repeat(BaseOption):
    """Maps configuration keys to identical sub-structures."""

    submodel: Union[BaseOption, dict, Callable[[str], Any]] = Option()


def load(
    model: Union[dict, Repeat],
    author: str,
    name: str,
    *args,
    env_prefix: Optional[str] = None,
    path: Union[None, PathLike, str, Sequence[Union[PathLike, str]]] = None,
    **kargs,
) -> dict:
    """Load configurations from multiple sources.

    Based on the model provided on the first argument,
    the function recursively searches for user configurations
    that can be defined in any source available.
    """
    path = cast_path(author, name, path)

    if env_prefix is None:
        env_prefix = name

    _search_config = partial(
        search_config, env_prefix=env_prefix, path=path, *args, **kargs
    )

    _repeat_subtree = partial(
        repeat_subtree, env_prefix=env_prefix, path=path, *args, **kargs
    )

    unlocated_keys = []
    invalid_keys = []
    expected_subtree_keys = []

    def _recurse(model, parent_keys):
        configs = {}
        for key, value in model.items():
            keys = parent_keys + [key]
            if isinstance(value, dict):
                config = _recurse(value, keys)
            elif isinstance(value, Option):
                try:
                    config = _search_config(keys, preprocess=value.preprocess)
                except ConfigNotFound:
                    config = value.default
                except InvalidOption as inv_opt:
                    config = inv_opt
                    invalid_keys.append(keys)
            elif isinstance(value, Required):
                try:
                    config = _search_config(keys, preprocess=value.preprocess)
                except ConfigNotFound:
                    config = InvalidOption(None, value)
                    unlocated_keys.append(keys)
                except InvalidOption as inv_opt:
                    config = inv_opt
                    invalid_keys.append(keys)
            elif isinstance(value, Repeat):
                try:
                    config = _recurse(_repeat_subtree(keys, value), keys)
                except InvalidOption as inv_opt:
                    config = inv_opt
                    expected_subtree_keys.append(keys)
            else:
                config = value
            configs[key] = config
        return configs

    if isinstance(model, dict):
        configs = _recurse(model, [])
    elif isinstance(model, Repeat):
        try:
            configs = _recurse(_repeat_subtree([], model), [])
        except InvalidOption as inv_opt:
            raise ConfigLoadingIncomplete([], [], [[]], inv_opt)

    if (
        len(unlocated_keys) != 0
        or len(invalid_keys) != 0
        or len(expected_subtree_keys) != 0
    ):
        raise ConfigLoadingIncomplete(
            unlocated_keys, invalid_keys, expected_subtree_keys, configs
        )

    return configs


def search_config(
    keys: List[str],
    env_prefix: str,
    path: List[Path],
    preprocess: Optional[Callable[[Any], Any]],
    *args,
    **kargs,
) -> Any:
    """Search a configuration variable from multiple sources."""
    if preprocess is None:
        preprocess = lambda x: x  # noqa: E731

    for location in path:
        for parser in default_parsers:
            try:
                value = preprocess(
                    parser.read(
                        keys=keys, path=location, env_prefix=env_prefix, *args, **kargs
                    )
                )
                return value
            except SkipSource:
                continue
            except InvalidOption:
                raise
            except Exception as err:
                raise ConfigReadingError from err

    raise ConfigNotFound


def repeat_subtree(
    keys: List[str],
    repeat: Repeat,
    env_prefix: str,
    path: List[Path],
    *args,
    **kargs,
) -> dict:
    """Compose repetition of configuration submodel."""
    root_keys = set()
    submodel = repeat.submodel
    get_submodel = submodel if callable(submodel) else lambda _: submodel

    for location in path:
        for parser in default_parsers:  # try to get all existing child keys
            try:
                root_keys.update(
                    parser.list_children(
                        keys=keys, path=location, env_prefix=env_prefix, *args, **kargs
                    )
                )
            except NotSubtree as not_subtree:
                raise InvalidOption(not_subtree.value, repeat) from not_subtree
            except Exception as err:
                raise ConfigReadingError from err
    return {key: get_submodel(key) for key in root_keys}


def cast_path(
    author: str,
    name: str,
    path: Union[PathLike, str, Sequence[Union[PathLike, str]], None],
) -> List[Path]:
    """Cast path given by user into List[Path] type."""
    if path is None:
        return default_path(author, name)
    if isinstance(path, list):
        return [Path(p) for p in path]
    if isinstance(path, (PathLike, str)):
        return [Path(path)]
    raise TypeError(
        "Argument path must be convertible to pathlib.Path or a list of such objects"
    )
