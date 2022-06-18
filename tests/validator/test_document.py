# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from pydoc import doc
from byteplug.validator import document_to_object
from byteplug.validator import ValidationError
import pytest

# Notes:
# - Keep this file in sync with test_object.py
#

def test_flag_type():
    specs = {'type': 'flag'}

    for value in ['42', '42.0', '"Hello world!"', '[]', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON boolean"

    object = document_to_object('false', specs)
    assert type(object) is bool
    assert object == False

    object = document_to_object('true', specs)
    assert type(object) is bool
    assert object == True

def test_integer_type():
    specs = {'type': 'integer'}

    for value in ['false', 'true', '"Hello world!"', '[]', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON number"

    for value in ['42', '42.0']:
        object = document_to_object(value, specs)
        assert type(object) is int
        assert object == 42

    # test if value is being checked against minimum value
    specs = {
        'type': 'integer',
        'minimum': 42
    }

    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("41", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or greater than X"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': False,
            'value': 42
        }
    }
    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("41", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or greater than X"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': True,
            'value': 42
        }
    }
    document_to_object("43", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("42", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be strictly greater than X"

    # test if value is being checked against maximum value
    specs = {
        'type': 'integer',
        'maximum': 42
    }

    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("43", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or less than X"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': False,
            'value': 42
        }
    }
    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("43", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or less than X"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': True,
            'value': 42
        }
    }
    document_to_object("41", specs)
    with pytest.raises(ValidationError) as e_info:
        document_to_object("42", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be strictly less than X"

def test_decimal_type():
    specs = {'type': 'decimal'}

def test_string_type():
    specs = {'type': 'string'}

    for value in ['false', 'true', '42', '42.0', '[]', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON string"

    object = document_to_object('"Hello world!"', specs)
    assert type(object) is str
    assert object == "Hello world!"

    # test if value is being checked against length value
    specs = {
        'type': 'string',
        'length': 42
    }

    value = 42 * 'a'
    document_to_object(f'"{value}"', specs)

    with pytest.raises(ValidationError) as e_info:
        value = 41* 'a'
        document_to_object(f'"{value}"', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of string must be equal to X"

    with pytest.raises(ValidationError) as e_info:
        value = 43 * 'a'
        document_to_object(f'"{value}"', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of string must be equal to X"

    specs = {
        'type': 'string',
        'length': {
            'minimum': 42
        }
    }

    value = 42 * 'a'
    document_to_object(f'"{value}"', specs)

    with pytest.raises(ValidationError) as e_info:
        value = 41* 'a'
        document_to_object(f'"{value}"', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of string must be greater or equal to X"

    specs = {
        'type': 'string',
        'length': {
            'maximum': 42
        }
    }

    value = 42 * 'a'
    document_to_object(f'"{value}"', specs)

    with pytest.raises(ValidationError) as e_info:
        value = 43* 'a'
        document_to_object(f'"{value}"', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of string must be lower or equal to X"

    # test if value is being checked against the pattern
    specs = {
        'type': 'string',
        'pattern': '^[a-z]+(-[a-z]+)*$'
    }

    for valid_value in ["foobar", "foo-bar"]:
        document_to_object(f'"{valid_value}"', specs)

    for invalid_value in ["Foobar", "foo_bar", "-foobar", "barfoo-", "foo--bar"]:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(f'"{invalid_value}"', specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "didnt match pattern"


def test_enum_type():
    specs = {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz']
    }

    for value in ['false', 'true', '42', '42.0', '[]', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON string"

    for value in ['foo', 'bar', 'quz']:
        object = document_to_object(f'"{value}"', specs)
        assert type(object) is str
        assert object == value

    # test if value is being checked against the valid values
    with pytest.raises(ValidationError) as e_info:
        document_to_object('"Hello world!"', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value was expected to be one of [foo, bar, quz]"

def test_list_type():
    specs = {'type': 'list', 'value': {'type': 'string'}}

    for value in ['false', 'true', '42', '42.0', '"Hello world!"', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON array"

    specs = {'type': 'list', 'value': {'type': 'flag'}}
    object = document_to_object('[true, false, true]', specs)
    assert type(object) is list
    assert object == [True, False, True]

    specs = {'type': 'list', 'value': {'type': 'integer'}}
    object = document_to_object('[10, 42, 100]', specs)
    assert type(object) is list
    assert object == [10, 42, 100]

    specs = {'type': 'list', 'value': {'type': 'string'}}
    object = document_to_object('["foo", "bar", "quz"]', specs)
    assert type(object) is list
    assert object == ["foo", "bar", "quz"]

    # test if list is being checked against length value
    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': 2
    }

    document_to_object('["foo", "bar"]', specs)

    with pytest.raises(ValidationError) as e_info:
        document_to_object('["foo"]', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of list must be equal to X"

    with pytest.raises(ValidationError) as e_info:
        document_to_object('["foo", "bar", "quz"]', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of list must be equal to X"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'minimum': 2
        }
    }
    document_to_object('["foo", "bar"]', specs)

    with pytest.raises(ValidationError) as e_info:
        document_to_object('["foo"]', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of list must be greater or equal to X"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'maximum': 2
        }
    }
    document_to_object('["foo", "bar"]', specs)

    with pytest.raises(ValidationError) as e_info:
        document_to_object('["foo", "bar", "quz"]', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of list must be lower or equal to X"


def test_tuple_type():
    specs = {
        'type': 'tuple',
        'values': [
            {'type': 'flag'},
            {'type': 'integer'},
            {'type': 'string'}
        ]
    }
    for value in ['false', 'true', '42', '42.0', '"Hello world!"', '{}']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON array"

    object = document_to_object('[true, 42, "foo"]', specs)
    assert type(object) is tuple
    assert object == (True, 42, "foo")

    with pytest.raises(ValidationError) as e_info:
        document_to_object('[false, true, 42, "foo"]', specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "was expecting array of N elements"


def test_map_type():
    specs = {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'integer'},
            'quz': {'type': 'string'}
        }
    }

    for value in ['false', 'true', '42', '42.0', '"Hello world!"', '[]']:
        with pytest.raises(ValidationError) as e_info:
            document_to_object(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a JSON object"

    object = document_to_object('{"foo": true, "bar": 42, "quz": "Hello world!"}', specs)
    assert type(object) is dict
    assert object == {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!"
    }

    # TODO; More things to test here.
