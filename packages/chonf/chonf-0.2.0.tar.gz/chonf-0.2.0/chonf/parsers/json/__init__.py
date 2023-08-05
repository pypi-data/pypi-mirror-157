# -*- coding: utf-8 -*-
# flake8: noqa F401 # <- allow unused imports, used here for namespace isolation
"""Provides access to json files.

The json syntax provides easy support for nested data. This
data is usually represented by a dictionary that can be
accessed as:

python: >>> toml_data['level1']['level2']['level3']

In a json file:

    {
        "level1": {
            "level2": {
                "level3": "value"
            }
        }
    }

With chonf, this will be accessed by:

python: >>> chonf.get(['level1', 'level2', 'level3'], *args, **kwargs)

Except when something else is found first that matches
the keys in some other configuration format, which will
short-circuit the search.

Functions:

    read(keys: List[str], dir_path: pathlib.Path, *args, **kargs) -> Any:
        Tries to read a configuration option from a Toml file.

"""
from chonf.parsers.json.core import read, list_children
