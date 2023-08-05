# -*- coding: utf-8 -*-
"""Provides exceptions for chonf.

Classes (exceptions):

    ConfigReadingError: Raised when an attempt to read a configuration fails
        in an unexpected manner.

    FileAccessError: Raised when an attempt to access a config file fails
        in an unexpected manner.

    SkipSource: Raised when an attempt to access a config source fails in an
        expected manner, so that chonf can continue looking elsewhere.

"""


from dataclasses import dataclass
from typing import Any, List, Union


class ConfigReadingError(Exception):
    """Configuration reading error.

    Throw when an attempt to access a configuration option fails
    in an unexpected manner, for a more comprehensive error log.
    """


class FileAccessError(Exception):
    """Configuration file access error.

    Throw when an attempt to read a configuration file fails in an
    unexpected manner, for a more comprehensive error log.

    Should not be confused with FileNotFoundError, as this exception
    is expected and should usually cause a SkipSource exception to
    be raised.
    """


class SkipSource(Exception):
    """Flow control exception to skip a configuration source.

    Throw when an attempt to access a configuration source fails
    in an expected way, to signify the getter to continue looking at
    other sources without stopping the program.
    """


class ConfigNotFound(Exception):
    """Configuration not found.

    Throw when an attempt to find a configuration option fails in
    all sources.
    """


@dataclass
class InvalidOption(Exception):
    """Info gathering exception for invalid configurations.

    Throw when a Option with validation finds a invalid value.
    Also works as a information dataclass to inform the problem
    in the configurations.
    """

    value: Any
    expected: Any


@dataclass
class ConfigLoadingIncomplete(Exception):
    """Configuration loading failed to complete.

    Throw when an attempt to load configurations fails to
    attend the defined constraints.
    """

    unlocated_keys: List[List[str]]
    invalid_keys: List[List[str]]
    expected_subtree_keys: List[List[str]]
    loaded_configs: Union[dict, InvalidOption]


class UnrecognizedOS(Exception):
    """Throw when the operational system is not recognized."""


@dataclass
class NotSubtree(Exception):
    """Info gathering exception for expected subtrees that aren't.

    Throw when trying to read a subtree structure such as a
    repeat, and finding a leaf node.
    """

    value: Any
