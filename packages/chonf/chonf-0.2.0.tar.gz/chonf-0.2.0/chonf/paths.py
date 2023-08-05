# -*- coding: utf-8 -*-
"""Provides default config paths for chonf.

Variables:

    default_path(author: str, name: str) -> List[pathlib.Path]:
        returns the paths to the user-wide and system-wide default
        configuration directories for the program running on the
        current system.

"""

from functools import cache
from os.path import expandvars
from pathlib import Path
from platform import system
from typing import List

from chonf.exceptions import UnrecognizedOS


@cache
def default_path(author: str, name: str) -> List[Path]:
    """Generate OS specific default config directory paths.

    Get the paths to the user-wide and system-wide default
    configuration directories for the program running on the
    current system.

    Args:
        author (str): Name of the author (company or person)
            of the program, used by Windows's default for
            program data files.
        name (str): Name of the program itself, that names
            the configuration directory under the system's
            default.
    """
    user_os = system()
    if user_os == "Linux":
        return [
            Path("~/.config/").expanduser() / name,
            Path("/etc/") / name,
        ]
    if user_os == "Windows":
        return [
            Path(expandvars("%APPDATA%")) / author / name,
            Path(expandvars("%PROGRAMDATA%")) / author / name,
        ]
    if user_os == "Darwin":  # macos
        return [
            Path("~/Library/Preferences/").expanduser() / name,
            Path("/Library/Preferences/") / name,
        ]
    raise UnrecognizedOS
