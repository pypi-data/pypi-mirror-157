# -*- coding: utf-8 -*-
"""Modules to parse different kinds of configurations."""
from chonf.parsers import envvars, python, toml, yaml, json, xml

default_parsers = [envvars, python, toml, yaml, json, xml]
