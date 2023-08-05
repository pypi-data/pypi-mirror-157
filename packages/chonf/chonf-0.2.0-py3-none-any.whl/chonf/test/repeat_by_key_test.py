# -*- coding: utf-8 -*-
import json

import pytest

import chonf
from chonf.core import Option, Repeat, Required
from chonf.exceptions import ConfigLoadingIncomplete, InvalidOption

"""Expected Behaviour:

Repeat objects should accept a by_key callable that receives a
string (the key of the repeating structure) and returns a valid
model branch to look for configurations with chonf. It also should
raise a special exception to signify that a key is not accepted
inside that Repeat.

This should be useful when, for example, a text editor would
read configurations for different language servers, but being
aware that some of them have special different options, and
maybe explicitly excluding any server that is not supported
so as to avoid users mistyping server names.

The signature should be something like:

by_key(key: str) -> dict | BaseOption

This should be enough to enable all sorts of crazy repeats
modulated by keys. Other conditions, depending on the contained
data, can be more generalized and applied to a more general case.

[replaning]
With a function to return the wanted model, it might be just better
to have a different class, say RepeatByKey, that would receive *only*
the function. The benefit of having a functional interface as basis
is that it allows for virtually any kind of crazy procedurally
generated models. The other option would be receiving a dictionary
of models, but that would be unwieldy to have a group of names
pointing to the same model, encouraging repeated code for beginer
programmers.

We could have Repeat recognize if the submodel is a callable,
and if so use it as a by_key function. This should reduce the
need for more classes for sure. Going with this.
"""


def by_key_modifier(key):
    if key in "abc":
        return Option()
    else:
        return {"a": Required()}


def test_branch_success(tmp_path):
    model = {"a": Repeat(by_key_modifier)}
    data = {"a": {"a": "a", "b": "b", "d": {"a": "a"}}}
    with open(tmp_path / "config.json", "w") as json_file:
        json.dump(data, json_file)
    configs = chonf.load(model, "me", "app", path=tmp_path)
    assert configs == data


def test_branch_fail(tmp_path):
    model = {"a": Repeat(by_key_modifier)}
    data = {"a": {"a": "a", "b": "b", "d": {}}}
    with open(tmp_path / "config.json", "w") as json_file:
        json.dump(data, json_file)
    with pytest.raises(ConfigLoadingIncomplete) as err:
        chonf.load(model, "me", "app", path=tmp_path)
    assert err.value.loaded_configs == {
        "a": {"a": "a", "b": "b", "d": {"a": InvalidOption(None, Required())}}
    }


def test_root_success(tmp_path):
    model = Repeat(by_key_modifier)
    data = {"a": "a", "b": "b", "d": {"a": "a"}}
    with open(tmp_path / "config.json", "w") as json_file:
        json.dump(data, json_file)
    configs = chonf.load(model, "me", "app", path=tmp_path)
    assert configs == data


def test_root_fail(tmp_path):
    model = Repeat(by_key_modifier)
    data = {"a": "a", "b": "b", "d": {}}
    with open(tmp_path / "config.json", "w") as json_file:
        json.dump(data, json_file)
    with pytest.raises(ConfigLoadingIncomplete) as err:
        chonf.load(model, "me", "app", path=tmp_path)
    assert err.value.loaded_configs == {
        "a": "a",
        "b": "b",
        "d": {"a": InvalidOption(None, Required())},
    }
