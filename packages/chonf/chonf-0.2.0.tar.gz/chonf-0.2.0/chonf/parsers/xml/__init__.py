# -*- coding: utf-8 -*-
# flake8: noqa F401 # <- allow unused imports, used here for namespace isolation
"""Provides access to xml files.

Functions:

    read(keys: List[str], path: pathlib.Path, *args, **kargs) -> Any:
        Tries to read a configuration option from a xml file.

"""
from chonf.parsers.xml.core import read, list_children
