# -*- coding: utf-8 -*-
import pytest
import majordome


def test_dict_get_nested_empty_dict():
    """ Call get_nested with empty dictionary. """
    with pytest.raises(KeyError):
        dict({}).get_nested()


def test_dict_get_nested_noarguments():
    """ Call get_nested with no arguments. """
    with pytest.raises(ValueError):
        dict({"a": 1}).get_nested()


def test_dict_get_nested_alright():
    """ Call get_nested with functioning arguments. """
    sample = dict({"a": {"b": {"c": 2}}})
    assert sample.get_nested("a", "b", "c") == 2

    sample = dict({"a": 2})
    assert sample.get_nested("a") == 2

    sample = dict({False: 2})
    assert sample.get_nested(False) == 2
