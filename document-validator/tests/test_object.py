# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document import object_to_document
from byteplug.document import ValidationError
import pytest

# Notes:
# - Keep this file in sync with test_document.py
#

VALID_NAMES = [
    "foobar",
    "foo-bar"
]

INVALID_NAMES = [
    "Foobar",
    "foo_bar",
    "-foobar",
    "barfoo-",
    "foo--bar"
]

def test_flag_type():
    specs = {'type': 'flag'}

    for value in [42, 42.0, "Hello world!", [], (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a boolean"

    document = object_to_document(False, specs)
    assert document == "false"

    document = object_to_document(True, specs)
    assert document == "true"

def test_integer_type():
    specs = {'type': 'integer'}

    for value in [False, True, 42.0, "Hello world!", [], (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting an integer"

    document = object_to_document(42, specs)
    assert document == "42"

    # test if value is being checked against minimum value
    specs = {
        'type': 'integer',
        'minimum': 42
    }

    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(41, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': False,
            'value': 42
        }
    }
    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(41, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': True,
            'value': 42
        }
    }
    object_to_document(43, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42, specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly greater than 42"

    # test if value is being checked against maximum value
    specs = {
        'type': 'integer',
        'maximum': 42
    }

    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(43, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': False,
            'value': 42
        }
    }
    object_to_document(42, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(43, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': True,
            'value': 42
        }
    }
    object_to_document(41, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42, specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly lower than 42"

    # test lazy validation
    specs = {
        'type': 'integer',
        'minimum': 43,
        'maximum': 41
    }

    errors = []
    object_to_document(42, specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "value must be equal or greater than 43"
    assert errors[1].path == []
    assert errors[1].message == "value must be equal or lower than 41"

def test_string_type():
    specs = {'type': 'string'}

    for value in [False, True, 42, 42.0, [], (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a string"

    document = object_to_document("Hello world!", specs)
    assert document == '"Hello world!"'

    # test if value is being checked against length value
    specs = {
        'type': 'string',
        'length': 42
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e:
        value = 41* 'a'
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 42"

    with pytest.raises(ValidationError) as e:
        value = 43 * 'a'
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 42"

    specs = {
        'type': 'string',
        'length': {
            'minimum': 42
        }
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e:
        value = 41* 'a'
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or greater than 42"

    specs = {
        'type': 'string',
        'length': {
            'maximum': 42
        }
    }

    value = 42 * 'a'
    object_to_document(value, specs)

    with pytest.raises(ValidationError) as e:
        value = 43* 'a'
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or lower than 42"

    # test if value is being checked against the pattern
    specs = {
        'type': 'string',
        'pattern': '^[a-z]+(-[a-z]+)*$'
    }

    for valid_value in ["foobar", "foo-bar"]:
        object_to_document(valid_value, specs)

    for invalid_value in ["Foobar", "foo_bar", "-foobar", "barfoo-", "foo--bar"]:
        with pytest.raises(ValidationError) as e:
            object_to_document(invalid_value, specs)
        assert e.value.path == []
        assert e.value.message == "value did not match the pattern"

    # test lazy validation
    specs = {
        'type': 'string',
        'length': 42,
        'pattern': "^[b-z]+$"
    }

    errors = []
    object_to_document(43* 'a', specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "length must be equal to 42"
    assert errors[1].path == []
    assert errors[1].message == "value did not match the pattern"

def test_array_type():
    specs = {'type': 'array', 'value': {'type': 'string'}}

    for value in [False, True, 42, 42.0, "Hello world!", (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a list"

    specs = {'type': 'array', 'value': {'type': 'flag'}}
    document = object_to_document([True, False, True], specs)
    assert document == '[true, false, true]'

    specs = {'type': 'array', 'value': {'type': 'integer'}}
    document = object_to_document([10, 42, 100], specs)
    assert document == '[10, 42, 100]'

    specs = {'type': 'array', 'value': {'type': 'string'}}
    document = object_to_document(["foo", "bar", "quz"], specs)
    assert document == '["foo", "bar", "quz"]'

    # test if array items are being checked against length value
    specs = {
        'type': 'array',
        'value': {'type': 'string'},
        'length': 2
    }

    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e:
        object_to_document(["foo"], specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    with pytest.raises(ValidationError) as e:
        object_to_document(["foo", "bar", "quz"], specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    specs = {
        'type': 'array',
        'value': {'type': 'string'},
        'length': {
            'minimum': 2
        }
    }
    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e:
        object_to_document(["foo"], specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or greater than 2"

    specs = {
        'type': 'array',
        'value': {'type': 'string'},
        'length': {
            'maximum': 2
        }
    }
    object_to_document(["foo", "bar"], specs)

    with pytest.raises(ValidationError) as e:
        object_to_document(["foo", "bar", "quz"], specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or lower than 2"

    # test lazy validation
    specs = {
        'type': 'array',
        'value': {'type': 'integer'},
    }

    errors = []
    object_to_document([True, 42, "Hello world!"], specs, errors=errors)

    assert errors[0].path == ["[0]"]
    assert errors[0].message == "was expecting an integer"
    assert errors[1].path == ["[2]"]
    assert errors[1].message == "was expecting an integer"

def test_object_type():
    specs = {
        'type': 'object',
        'key': 'string',
        'value': {
            'type': 'string'
        }
    }

    for value in [False, True, 42, 42.0, "Hello world!", [], ()]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a dict"

    # test with key set to 'integer'
    specs = {'type': 'object', 'key': 'integer', 'value': {'type': 'string'}}

    document = object_to_document({1: "foo", 2: "bar", 3: "quz"}, specs)
    assert document == '{"1": "foo", "2": "bar", "3": "quz"}'

    with pytest.raises(ValidationError) as e:
        object_to_document({1: "foo", 2.5: "bar", 3: "quz"}, specs)
    assert e.value.path == []
    assert e.value.message == "key at index 1 is invalid; expected it to be an integer"

    with pytest.raises(ValidationError) as e:
        object_to_document({1: "foo", "bar": "bar", 3: "quz"}, specs)
    assert e.value.path == []
    assert e.value.message == "key at index 1 is invalid; expected it to be an integer"

    # test with key set to 'string'
    specs = {'type': 'object', 'key': 'string', 'value': {'type': 'integer'}}

    for name in VALID_NAMES:
        document = object_to_document({'foo': 10, name: 42, 'quz': 100}, specs)
        assert document == '{"foo": 10, "name": 42, "quz": 100}'.replace('name', name)

    for name in INVALID_NAMES:
        with pytest.raises(ValidationError) as e:
            document = object_to_document({'foo': 10, name: 42, 'quz': 100}, specs)
        assert e.value.path == []
        assert e.value.message == "key at index 1 is invalid; expected to match the pattern"

    # test if object items are being checked against length value
    specs = {
        'type': 'object',
        'key': 'string',
        'value': {'type': 'integer'},
        'length': 2
    }

    object_to_document({'foo': 1, 'bar': 2}, specs)

    with pytest.raises(ValidationError) as e:
        object_to_document({'foo': 1}, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    with pytest.raises(ValidationError) as e:
        object_to_document({'foo': 1, 'bar': 2, 'quz': 3}, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    specs = {
        'type': 'object',
        'key': 'string',
        'value': {'type': 'integer'},
        'length': {
            'minimum': 2
        }
    }
    object_to_document({'foo': 1, 'bar': 2}, specs)

    with pytest.raises(ValidationError) as e:
        object_to_document({'foo': 1}, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or greater than 2"

    specs = {
        'type': 'object',
        'key': 'string',
        'value': {'type': 'integer'},
        'length': {
            'maximum': 2
        }
    }
    object_to_document({'foo': 1, 'bar': 2}, specs)

    with pytest.raises(ValidationError) as e:
        object_to_document({'foo': 1, 'bar': 2, 'quz': 3}, specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or lower than 2"

    # test lazy validation
    specs = {
        'type': 'object',
        'key': 'string',
        'value': {'type': 'integer'},
    }

    errors = []
    object_to_document({'foo': True, 'bar': 42, 'quz': "Hello world!"}, specs, errors=errors)

    assert errors[0].path == ["{foo}"]
    assert errors[0].message == "was expecting an integer"
    assert errors[1].path == ["{quz}"]
    assert errors[1].message == "was expecting an integer"

def test_tuple_type():
    specs = {
        'type': 'tuple',
        'items': [
            {'type': 'flag'},
            {'type': 'integer'},
            {'type': 'string'}
        ]
    }
    for value in [False, True, 42, 42.0, "Hello world!", [], {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a tuple"

    document = object_to_document((True, 42, "foo"), specs)
    assert document == '[true, 42, "foo"]'

    with pytest.raises(ValidationError) as e:
        object_to_document((False, True, 42, "foo"), specs)
    assert e.value.path == []
    assert e.value.message == "length of the tuple must be 3"

    # test lazy validation
    errors = []
    object_to_document(("foo", True, 42), specs, errors=errors)
    assert errors[0].path == ["<0>"]
    assert errors[0].message == "was expecting a boolean"
    assert errors[1].path == ["<1>"]
    assert errors[1].message == "was expecting an integer"
    assert errors[2].path == ["<2>"]
    assert errors[2].message == "was expecting a string"

def test_map_type():
    specs = {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {
                'type': 'integer',
                'option': True
            },
            'quz': {'type': 'string'}
        }
    }

    for value in [False, True, 42, 42.0, "Hello world!", [], ()]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a dict"

    value = {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!"
    }
    document = object_to_document(value, specs)
    assert document == '{"foo": true, "bar": 42, "quz": "Hello world!"}'

    # test if non-string keys are reported
    value = {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!",
        42: False
    }
    with pytest.raises(ValidationError) as e:
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "keys of the dict must be string exclusively"

    # test if unexpected fields are reported
    value = {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!",
        "yolo": False
    }
    with pytest.raises(ValidationError) as e:
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "'yolo' field was unexpected"

    # test if missing fields are reported
    value = {
        "foo": True,
        "bar": 42
    }
    with pytest.raises(ValidationError) as e:
        object_to_document(value, specs)
    assert e.value.path == []
    assert e.value.message == "'quz' field was missing"

    # test if missing optional fields are NOT reported
    value = {
        "foo": True,
        "quz": "Hello world!"
    }
    document = object_to_document(value, specs)
    # TODO; Note that the order is not preserved. Implementation can be changed
    #       in order to keep it.
    assert document == '{"foo": true, "quz": "Hello world!", "bar": null}'

    # test lazy validation
    errors = []

    value = {
        "foo": "Hello world!",
        "bar": True,
        "quz": 42
    }
    object_to_document(value, specs, errors=errors)
    assert errors[0].path == ["$foo"]
    assert errors[0].message == "was expecting a boolean"
    assert errors[1].path == ["$bar"]
    assert errors[1].message == "was expecting an integer"
    assert errors[2].path == ["$quz"]
    assert errors[2].message == "was expecting a string"

def test_decimal_type():
    specs = {'type': 'decimal'}

    for value in [False, True, 42, "Hello world!", [], (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a float"

    document = object_to_document(42.5, specs)
    assert document == "42.5"

    # test if value is being checked against minimum value
    specs = {
        'type': 'decimal',
        'minimum': 42.5
    }

    object_to_document(42.5, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.4, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42.5"

    specs = {
        'type': 'decimal',
        'minimum': {
            'exclusive': False,
            'value': 42.5
        }
    }
    object_to_document(42.5, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.4, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42.5"

    specs = {
        'type': 'decimal',
        'minimum': {
            'exclusive': True,
            'value': 42.5
        }
    }
    object_to_document(42.6, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.5, specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly greater than 42.5"

    # test if value is being checked against maximum value
    specs = {
        'type': 'decimal',
        'maximum': 42.5
    }

    object_to_document(42.5, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.6, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42.5"

    specs = {
        'type': 'decimal',
        'maximum': {
            'exclusive': False,
            'value': 42.5
        }
    }
    object_to_document(42.5, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.6, specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42.5"

    specs = {
        'type': 'decimal',
        'maximum': {
            'exclusive': True,
            'value': 42.5
        }
    }
    object_to_document(42.4, specs)
    with pytest.raises(ValidationError) as e:
        object_to_document(42.5, specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly lower than 42.5"

    # test lazy validation
    specs = {
        'type': 'decimal',
        'minimum': 42.75,
        'maximum': 42.25
    }

    errors = []
    object_to_document(42.5, specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "value must be equal or greater than 42.75"
    assert errors[1].path == []
    assert errors[1].message == "value must be equal or lower than 42.25"

def test_enum_type():
    specs = {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz']
    }

    for value in [False, True, 42, 42.0, [], (), {}]:
        with pytest.raises(ValidationError) as e:
            object_to_document(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a string"

    for value in ['foo', 'bar', 'quz']:
        document = object_to_document(value, specs)
        assert document == f'"{value}"'

    # test if value is being checked against the valid values
    with pytest.raises(ValidationError) as e:
        object_to_document("Hello world!", specs)
    assert e.value.path == []
    assert e.value.message == "enum value is invalid"
