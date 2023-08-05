# -*- coding: utf-8 -*-
# flake8: noqa F401 # <- allow unused imports, used here for namespace isolation
"""Utilities for accessing user configurations from multiple posible sources.

Functions:

    * load - Tries to load user configurations from multiple sources
    * default_path - Generates list of default config file locations, OS aware

"""
from chonf.core import load, Option, Required, Repeat
from chonf.exceptions import ConfigReadingError, ConfigLoadingIncomplete, InvalidOption
from chonf.paths import default_path
