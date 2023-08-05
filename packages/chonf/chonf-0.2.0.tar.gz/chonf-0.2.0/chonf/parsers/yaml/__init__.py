# -*- coding: utf-8 -*-
# flake8: noqa F401 # <- allow unused imports, used here for namespace isolation
"""Provides access to yaml files.

Functions:

    read(keys: List[str], path: pathlib.Path, *args, **kargs) -> Any:
        Tries to read a configuration option from a yaml file.

"""
from chonf.parsers.yaml.core import read, list_children
