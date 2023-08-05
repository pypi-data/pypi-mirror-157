# -*- coding: utf-8 -*-
import json

import pytest

from chonf import ConfigLoadingIncomplete, Option, Repeat, Required, load
from chonf.exceptions import InvalidOption

MODEL = {
    "option_a": Option(),
    "option_b": Option(),
    "option_repeat": Repeat(Option()),
    "empty_repeat": Repeat(Option()),
    "users": Repeat(
        {
            "name": Required(),
            "nick": Option(),
        }
    ),
}

VALID_DATA = {
    "option_a": "value_a",
    "option_b": "value_b",
    "option_repeat": {"a": "a", "b": "b", "c": "c"},
    "empty_repeat": {},
    "users": {
        "user_1": {
            "name": "Jean Jacques Rousseau",
            "nick": "Jack",
        },
        "user_2": {
            "name": "Mary Wollstonecraft",
        },
        "user_3": {"name": "James Hoffman", "nick": "Internet Coffee Dude"},
    },
}

INVALID_DATA = {
    "option_a": "value_a",
    "option_b": "value_b",
    "option_repeat": "invalid_value",  # this should be a subtree
    "empty_repeat": {},
    "users": {
        "user_1": {
            "name": "Jean Jacques Rousseau",
            "nick": "Jack",
        },
        "user_2": {
            "nick": "Did she have a nickname?",  # no name on this one
        },
        "user_3": {"name": "James Hoffman", "nick": "Internet Coffee Dude"},
    },
}


@pytest.fixture(scope="module")
def valid_conf_dir(tmp_path_factory):
    dir_path = tmp_path_factory.mktemp("chonf_repeat_test_valid")
    with open(dir_path / "config.json", "w") as f:
        json.dump(VALID_DATA, f)
    return dir_path


@pytest.fixture(scope="module")
def invalid_conf_dir(tmp_path_factory):
    dir_path = tmp_path_factory.mktemp("chonf_repeat_test_invalid")
    with open(dir_path / "config.json", "w", encoding="utf-8") as json_file:
        json.dump(INVALID_DATA, json_file)
    return dir_path


@pytest.fixture(scope="module")
def valid_conf_data(valid_conf_dir):
    return load(MODEL, author="me", name="mock", path=valid_conf_dir)


def test_valid_data(valid_conf_data):
    assert valid_conf_data == {
        "option_a": "value_a",
        "option_b": "value_b",
        "option_repeat": {"a": "a", "b": "b", "c": "c"},
        "empty_repeat": {},
        "users": {
            "user_1": {
                "name": "Jean Jacques Rousseau",
                "nick": "Jack",
            },
            "user_2": {
                "name": "Mary Wollstonecraft",
                "nick": None,  # here the not found value reads to None
            },
            "user_3": {"name": "James Hoffman", "nick": "Internet Coffee Dude"},
        },
    }


@pytest.fixture(scope="module")
def invalid_data_error(invalid_conf_dir):
    with pytest.raises(ConfigLoadingIncomplete) as err:
        load(MODEL, author="me", name="mock", path=invalid_conf_dir)
    return err.value


def test_invalid_data_loaded_configs(invalid_data_error):
    assert invalid_data_error.loaded_configs == {
        "option_a": "value_a",
        "option_b": "value_b",
        "option_repeat": InvalidOption("invalid_value", Repeat(Option())),
        "empty_repeat": {},
        "users": {
            "user_1": {
                "name": "Jean Jacques Rousseau",
                "nick": "Jack",
            },
            "user_2": {
                "name": InvalidOption(None, Required()),
                "nick": "Did she have a nickname?",  # no name on this one
            },
            "user_3": {"name": "James Hoffman", "nick": "Internet Coffee Dude"},
        },
    }


def test_root_repeat(tmp_path):
    data = {
        "aaa": {"a": "a", "b": "b", "c": "c"},
        "bbb": {"a": "a", "b": "b", "c": "c"},
        "ccc": {"a": "a", "b": "b", "c": "c"},
    }
    with open(tmp_path / "config.json", "w", encoding="utf-8") as file:
        json.dump(data, file)
    model = Repeat({"a": Option(), "b": Option(), "c": Option()})
    configs = load(model, "me", "app", path=tmp_path)
    assert configs == {
        "aaa": {"a": "a", "b": "b", "c": "c"},
        "bbb": {"a": "a", "b": "b", "c": "c"},
        "ccc": {"a": "a", "b": "b", "c": "c"},
    }


def test_root_repeat_empty(tmp_path):
    data = {}
    with open(tmp_path / "config.json", "w", encoding="utf-8") as file:
        json.dump(data, file)
    model = Repeat({"a": Option(), "b": Option(), "c": Option()})
    configs = load(model, "me", "app", path=tmp_path)
    assert configs == {}
