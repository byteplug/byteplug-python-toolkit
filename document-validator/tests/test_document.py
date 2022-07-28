# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document import document_to_object
from byteplug.document import ValidationError
import pytest

# Notes:
# - Keep this file in sync with test_object.py
#

def test_flag_type():
    specs = {'type': 'flag'}

    for value in ['42', '42.0', '"Hello world!"', '[]', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON boolean"

    object = document_to_object('false', specs)
    assert type(object) is bool
    assert object == False

    object = document_to_object('true', specs)
    assert type(object) is bool
    assert object == True

def test_integer_type():
    specs = {'type': 'integer'}

    for value in ['false', 'true', '"Hello world!"', '[]', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON number"

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
    with pytest.raises(ValidationError) as e:
        document_to_object("41", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': False,
            'value': 42
        }
    }
    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("41", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42"

    specs = {
        'type': 'integer',
        'minimum': {
            'exclusive': True,
            'value': 42
        }
    }
    document_to_object("43", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42", specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly greater than 42"

    # test if value is being checked against maximum value
    specs = {
        'type': 'integer',
        'maximum': 42
    }

    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("43", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': False,
            'value': 42
        }
    }
    document_to_object("42", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("43", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42"

    specs = {
        'type': 'integer',
        'maximum': {
            'exclusive': True,
            'value': 42
        }
    }
    document_to_object("41", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42", specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly lower than 42"

    # check if warning is raised when it's a decimal value
    warnings = []
    object = document_to_object("42.5", {'type': 'integer'}, warnings=warnings)
    assert type(object) is int
    assert object == 42

    assert len(warnings) == 1
    assert warnings[0].path == []
    assert warnings[0].message == "may lose precision"

    # test lazy validation
    specs = {
        'type': 'integer',
        'minimum': 43,
        'maximum': 41
    }

    errors = []
    document_to_object("42", specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "value must be equal or greater than 43"
    assert errors[1].path == []
    assert errors[1].message == "value must be equal or lower than 41"

def test_string_type():
    specs = {'type': 'string'}

    for value in ['false', 'true', '42', '42.0', '[]', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON string"

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

    with pytest.raises(ValidationError) as e:
        value = 41* 'a'
        document_to_object(f'"{value}"', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 42"

    with pytest.raises(ValidationError) as e:
        value = 43 * 'a'
        document_to_object(f'"{value}"', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 42"

    specs = {
        'type': 'string',
        'length': {
            'minimum': 42
        }
    }

    value = 42 * 'a'
    document_to_object(f'"{value}"', specs)

    with pytest.raises(ValidationError) as e:
        value = 41* 'a'
        document_to_object(f'"{value}"', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or greater than 42"

    specs = {
        'type': 'string',
        'length': {
            'maximum': 42
        }
    }

    value = 42 * 'a'
    document_to_object(f'"{value}"', specs)

    with pytest.raises(ValidationError) as e:
        value = 43* 'a'
        document_to_object(f'"{value}"', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or lower than 42"

    # test if value is being checked against the pattern
    specs = {
        'type': 'string',
        'pattern': '^[a-z]+(-[a-z]+)*$'
    }

    for valid_value in ["foobar", "foo-bar"]:
        document_to_object(f'"{valid_value}"', specs)

    for invalid_value in ["Foobar", "foo_bar", "-foobar", "barfoo-", "foo--bar"]:
        with pytest.raises(ValidationError) as e:
            document_to_object(f'"{invalid_value}"', specs)
        assert e.value.path == []
        assert e.value.message == "value did not match the pattern"

    # test lazy validation
    specs = {
        'type': 'string',
        'length': 42,
        'pattern': "^[b-z]+$"
    }

    errors = []

    value = 43* 'a'
    document_to_object(f'"{value}"', specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "length must be equal to 42"
    assert errors[1].path == []
    assert errors[1].message == "value did not match the pattern"

def test_list_type():
    specs = {'type': 'list', 'value': {'type': 'string'}}

    for value in ['false', 'true', '42', '42.0', '"Hello world!"', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON array"

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

    with pytest.raises(ValidationError) as e:
        document_to_object('["foo"]', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    with pytest.raises(ValidationError) as e:
        document_to_object('["foo", "bar", "quz"]', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal to 2"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'minimum': 2
        }
    }
    document_to_object('["foo", "bar"]', specs)

    with pytest.raises(ValidationError) as e:
        document_to_object('["foo"]', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or greater than 2"

    specs = {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'maximum': 2
        }
    }
    document_to_object('["foo", "bar"]', specs)

    with pytest.raises(ValidationError) as e:
        document_to_object('["foo", "bar", "quz"]', specs)
    assert e.value.path == []
    assert e.value.message == "length must be equal or lower than 2"

    # test lazy validation
    specs = {
        'type': 'list',
        'value': {'type': 'integer'},
    }

    errors = []
    document_to_object('[true, 42, "Hello world!"]', specs, errors=errors)

    assert errors[0].path == ["[0]"]
    assert errors[0].message == "was expecting a JSON number"
    assert errors[1].path == ["[2]"]
    assert errors[1].message == "was expecting a JSON number"

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
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON array"

    object = document_to_object('[true, 42, "foo"]', specs)
    assert type(object) is tuple
    assert object == (True, 42, "foo")

    with pytest.raises(ValidationError) as e:
        document_to_object('[false, true, 42, "foo"]', specs)
    assert e.value.path == []
    assert e.value.message == "length of the array must be 3"

    # test lazy validation
    errors = []
    document_to_object('["foo", true, 42]', specs, errors=errors)
    assert errors[0].path == ["(0)"]
    assert errors[0].message == "was expecting a JSON boolean"
    assert errors[1].path == ["(1)"]
    assert errors[1].message == "was expecting a JSON number"
    assert errors[2].path == ["(2)"]
    assert errors[2].message == "was expecting a JSON string"

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
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON object"

    object = document_to_object('{"foo": true, "bar": 42, "quz": "Hello world!"}', specs)
    assert type(object) is dict
    assert object == {
        "foo": True,
        "bar": 42,
        "quz": "Hello world!"
    }

    # test if unexpected fields are reported
    with pytest.raises(ValidationError) as e:
        document_to_object('{"foo": true, "bar": 42, "quz": "Hello world!", "yolo": false}', specs)
    assert e.value.path == []
    assert e.value.message == "'yolo' field was unexpected"

    # test if missing fields are reported
    with pytest.raises(ValidationError) as e:
        document_to_object('{"foo": true, "bar": 42}', specs)
    assert e.value.path == []
    assert e.value.message == "'quz' field was missing"

    # test lazy validation
    errors = []
    document_to_object('{"foo": "Hello world!", "bar": true, "quz": 42}', specs, errors=errors)
    assert errors[0].path == ["{foo}"]
    assert errors[0].message == "was expecting a JSON boolean"
    assert errors[1].path == ["{bar}"]
    assert errors[1].message == "was expecting a JSON number"
    assert errors[2].path == ["{quz}"]
    assert errors[2].message == "was expecting a JSON string"


def test_decimal_type():
    specs = {'type': 'decimal'}

    for value in ['false', 'true', '"Hello world!"', '[]', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON number"

    for value in ['42', '42.0']:
        object = document_to_object(value, specs)
        assert type(object) is float
        assert object == 42.0

    # test if value is being checked against minimum value
    specs = {
        'type': 'decimal',
        'minimum': 42.5
    }

    document_to_object("42.5", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.4", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42.5"

    specs = {
        'type': 'decimal',
        'minimum': {
            'exclusive': False,
            'value': 42.5
        }
    }
    document_to_object("42.5", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.4", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or greater than 42.5"

    specs = {
        'type': 'decimal',
        'minimum': {
            'exclusive': True,
            'value': 42.5
        }
    }
    document_to_object("42.6", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.5", specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly greater than 42.5"

    # test if value is being checked against maximum value
    specs = {
        'type': 'decimal',
        'maximum': 42.5
    }

    document_to_object("42.5", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.6", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42.5"

    specs = {
        'type': 'decimal',
        'maximum': {
            'exclusive': False,
            'value': 42.5
        }
    }
    document_to_object("42.5", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.6", specs)
    assert e.value.path == []
    assert e.value.message == "value must be equal or lower than 42.5"

    specs = {
        'type': 'decimal',
        'maximum': {
            'exclusive': True,
            'value': 42.5
        }
    }
    document_to_object("42.4", specs)
    with pytest.raises(ValidationError) as e:
        document_to_object("42.5", specs)
    assert e.value.path == []
    assert e.value.message == "value must be strictly lower than 42.5"

    # test lazy validation
    specs = {
        'type': 'decimal',
        'minimum': 42.75,
        'maximum': 42.25
    }

    errors = []
    document_to_object("42.5", specs, errors=errors)
    assert errors[0].path == []
    assert errors[0].message == "value must be equal or greater than 42.75"
    assert errors[1].path == []
    assert errors[1].message == "value must be equal or lower than 42.25"

def test_enum_type():
    specs = {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz']
    }

    for value in ['false', 'true', '42', '42.0', '[]', '{}']:
        with pytest.raises(ValidationError) as e:
            document_to_object(value, specs)
        assert e.value.path == []
        assert e.value.message == "was expecting a JSON string"

    for value in ['foo', 'bar', 'quz']:
        object = document_to_object(f'"{value}"', specs)
        assert type(object) is str
        assert object == value

    # test if value is being checked against the valid values
    with pytest.raises(ValidationError) as e:
        document_to_object('"Hello world!"', specs)
    assert e.value.path == []
    assert e.value.message == "enum value is invalid"
