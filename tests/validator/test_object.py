# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.validator import object_to_document
from byteplug.validator import ValidationError
import pytest

# Notes:
# - Keep this file in sync with test_document.py
#

def test_flag_type():
    specs = {'type': 'flag'}

    for value in [42, 42.0, "Hello world!", [], (), {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a boolean"

    document = object_to_document(False, specs)
    assert document == "false"

    document = object_to_document(True, specs)
    assert document == "true"

def test_integer_type():
    specs = {'type': 'integer'}

    for value in [False, True, 42.0, "Hello world!", [], (), {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting an integer"

    document = object_to_document(42, specs)
    assert document == "42"

    # test if value is being checked against minimum value
    specs = {
        'type': 'integer',
        'minimum': 42
    }

    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(41, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': False,
            'value': 42
        }
    }
    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(41, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': True,
            'value': 42
        }
    }
    object_to_document(43, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(42, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be strictly greater than 42"

    # test if value is being checked against maximum value
    specs = {
        'type': 'integer',
        'maximum': 42
    }

    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(43, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': False,
            'value': 42
        }
    }
    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(43, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': True,
            'value': 42
        }
    }
    object_to_document(41, specs)
    with pytest.raises(ValidationError) as e_info:
        object_to_document(42, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "value must be strictly lower than 42"

    # test lazy validation
    specs = {
        'type': 'integer',
        'minimum': 43,
        'maximum': 41
    }

    errors = []
    object_to_document(42, specs, errors=errors)
    assert errors[0].path == "root"
    assert errors[0].message == "value must be equal or greater than 43"
    assert errors[1].path == "root"
    assert errors[1].message == "value must be equal or lower than 41"

def test_decimal_type():
    pass

def test_string_type():
    specs = {'type': 'string'}

    for value in [False, True, 42, 42.0, [], (), {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a string"

    document = object_to_document("Hello world!", specs)
    assert document == '"Hello world!"'

    # test if value is being checked against length value
    specs = {
        'type': 'string',
        'length': 42
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e_info:
        value = 41* 'a'
        object_to_document(value, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal to 42"

    with pytest.raises(ValidationError) as e_info:
        value = 43 * 'a'
        object_to_document(value, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal to 42"

    specs = {
        'type': 'string',
        'length': {
            'minimum': 42
        }
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e_info:
        value = 41* 'a'
        object_to_document(value, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal or greater than 42"

    specs = {
        'type': 'string',
        'length': {
            'maximum': 42
        }
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e_info:
        value = 43* 'a'
        object_to_document(value, specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal or lower than 42"

    # test if value is being checked against the pattern
    specs = {
        'type': 'string',
        'pattern': '^[a-z]+(-[a-z]+)*$'
    }

    for valid_value in ["foobar", "foo-bar"]:
        object_to_document(valid_value, specs)

    for invalid_value in ["Foobar", "foo_bar", "-foobar", "barfoo-", "foo--bar"]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(invalid_value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "value did not match the pattern"

    # test lazy validation
    specs = {
        'type': 'string',
        'length': 42,
        'pattern': "^[b-z]+$"
    }

    errors = []
    object_to_document(43* 'a', specs, errors=errors)
    assert errors[0].path == "root"
    assert errors[0].message == "length must be equal to 42"
    assert errors[1].path == "root"
    assert errors[1].message == "value did not match the pattern"

def test_enum_type():
    specs = {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz']
    }

    for value in [False, True, 42, 42.0, [], (), {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a string"

    for value in ['foo', 'bar', 'quz']:
        document = object_to_document(value, specs)
        assert document == f'"{value}"'

    # test if value is being checked against the valid values
    with pytest.raises(ValidationError) as e_info:
        object_to_document("Hello world!", specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "enum value is invalid"

def test_list_type():
    specs = {'type': 'list', 'value': {'type': 'string'}}

    for value in [False, True, 42, 42.0, "Hello world!", (), {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a list"

    specs = {'type': 'list', 'value': {'type': 'flag'}}
    document = object_to_document([True, False, True], specs)
    assert document == '[true, false, true]'

    specs = {'type': 'list', 'value': {'type': 'integer'}}
    document = object_to_document([10, 42, 100], specs)
    assert document == '[10, 42, 100]'

    specs = {'type': 'list', 'value': {'type': 'string'}}
    document = object_to_document(["foo", "bar", "quz"], specs)
    assert document == '["foo", "bar", "quz"]'

    # test if list is being checked against length value
    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': 2
    }

    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e_info:
        object_to_document(["foo"], specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal to 2"

    with pytest.raises(ValidationError) as e_info:
        object_to_document(["foo", "bar", "quz"], specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal to 2"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'minimum': 2
        }
    }
    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e_info:
        object_to_document(["foo"], specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal or greater than 2"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'maximum': 2
        }
    }
    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e_info:
        object_to_document(["foo", "bar", "quz"], specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length must be equal or lower than 2"

    # test lazy validation
    specs = {
        'type': 'list',
        'value': {'type': 'integer'},
    }

    errors = []
    object_to_document([True, 42, "Hello world!"], specs, errors=errors)

    assert errors[0].path == "root.[0]"
    assert errors[0].message == "was expecting an integer"
    assert errors[1].path == "root.[2]"
    assert errors[1].message == "was expecting an integer"

def test_tuple_type():
    specs = {
        'type': 'tuple',
        'values': [
            {'type': 'flag'},
            {'type': 'integer'},
            {'type': 'string'}
        ]
    }
    for value in [False, True, 42, 42.0, "Hello world!", [], {}]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a tuple"

    document = object_to_document((True, 42, "foo"), specs)
    assert document == '[true, 42, "foo"]'

    with pytest.raises(ValidationError) as e_info:
        object_to_document((False, True, 42, "foo"), specs)
    assert e_info.value.path == "root"
    assert e_info.value.message == "length of the tuple must be 3"

    # test lazy validation
    errors = []
    object_to_document(("foo", True, 42), specs, errors=errors)
    assert errors[0].path == "root.(0)"
    assert errors[0].message == "was expecting a boolean"
    assert errors[1].path == "root.(1)"
    assert errors[1].message == "was expecting an integer"
    assert errors[2].path == "root.(2)"
    assert errors[2].message == "was expecting a string"

def test_map_type():
    specs = {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'integer'},
            'quz': {'type': 'string'}
        }
    }

    for value in [False, True, 42, 42.0, "Hello world!", [], ()]:
        with pytest.raises(ValidationError) as e_info:
            object_to_document(value, specs)
        assert e_info.value.path == "root"
        assert e_info.value.message == "was expecting a dict"

    value = {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!"
    }
    document = object_to_document(value, specs)
    assert document == '{"foo": true, "bar": 42, "quz": "Hello world!"}'

    # TODO; More things to test here.

    # test lazy validation
    errors = []

    value = {
        "foo": "Hello world!",
        "bar": True,
        "quz": 42
    }
    object_to_document(value, specs, errors=errors)
    assert errors[0].path == "root.foo"
    assert errors[0].message == "was expecting a boolean"
    assert errors[1].path == "root.bar"
    assert errors[1].message == "was expecting an integer"
    assert errors[2].path == "root.quz"
    assert errors[2].message == "was expecting a string"
