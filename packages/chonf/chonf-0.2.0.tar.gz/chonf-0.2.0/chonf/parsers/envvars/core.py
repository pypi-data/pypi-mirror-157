# -*- coding: utf-8 -*-
"""Core functionality for the environment variable parser.

Functions:

    read(keys, *args, **kargs) -> str:
        Tries to read a configuration option from an environment variable.

"""
import os
import re
from typing import List, Set

from chonf.exceptions import NotSubtree, SkipSource


def read(keys: List[str], env_prefix: str, *_, **__) -> str:
    """Read configuration option from environment variable.

    Args:
        keys (List[str]): Sequence of keys to construct the env var name.
        env_prefix (str): Prefix of the env var name

    Returns:
        str: The env var value.

    Raises:
        SkipSource: For expected problems, to be ignored and skipped.

    """
    try:
        return os.environ["__".join([env_prefix, *keys])]
    except KeyError as err:
        raise SkipSource from err


def list_children(keys: List[str], env_prefix: str, *_, **__) -> Set[str]:
    """List all children keys of a given key from env vars."""
    parent_key = "__".join([env_prefix, *keys])
    children = set()
    for key, value in os.environ.items():
        if key == parent_key:
            raise NotSubtree(value)  # error when key is for a leaf node (not a dict)
        if key.startswith(parent_key):
            child = re.split("__", key)[len(keys) + 1]
            children.add(child)
    return children
