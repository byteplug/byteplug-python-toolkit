# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document import validate_specs
from byteplug.document import ValidationError
import pytest

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

def dict_minus_item(a, key):
    b = a.copy()
    b.pop(key)
    return b

def bool_value_property_test(specs, key, path):
    validate_specs(specs | {key: True})
    validate_specs(specs | {key: False})

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: 42})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a bool"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: "Hello world!"})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a bool"

def number_value_property_test(specs, key, path):
    validate_specs(specs | {key: 42})

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: False})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a number"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: True})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a number"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: "Hello world!"})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a number"

def string_value_property_test(specs, key, path):
    validate_specs(specs | {key: "Hello world!"})

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: False})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a string"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: True})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a string"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {key: 42})
    assert e.value.path == path + [key]
    assert e.value.message == f"value must be a string"

def missing_property_test(specs, property):
    with pytest.raises(ValidationError) as e:
        validate_specs(specs)
    assert e.value.path == []
    assert e.value.message == f"'{property}' property is missing"

def name_property_test(specs):
    # validate_specs(specs | {'foo': 'bar', 'bar': 'foo'})
    string_value_property_test(specs, "name", [])

def description_property_test(specs):
    string_value_property_test(specs, "description", [])

def length_property_test(specs):
    validate_specs(specs | {'length': 42})

    validate_specs(specs | {'length': {'minimum': 42}})
    validate_specs(specs | {'length': {'maximum': 42}})
    validate_specs(specs | {'length': {'minimum': 0, 'maximum': 42}})

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'length': -1})
    assert e.value.path == ["length"]
    assert e.value.message == "must be greater or equal to zero"

    warnings = []
    validate_specs(specs | {'length': 42.5}, warnings=warnings)
    assert len(warnings) == 1
    assert warnings[0].path == ["length"]
    assert warnings[0].message == "should be an integer (got float)"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'length': {'minimum': -1}})
    assert e.value.path == ["length", "minimum"]
    assert e.value.message == "must be greater or equal to zero"

    warnings = []
    validate_specs(specs | {'length': {'minimum': 42.5}}, warnings=warnings)
    assert len(warnings) == 1
    assert warnings[0].path == ["length"]
    assert warnings[0].message == "should be an integer (got float)"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'length': {'maximum': -1}})
    assert e.value.path == ["length", "maximum"]
    assert e.value.message == "must be greater or equal to zero"

    warnings = []
    validate_specs(specs | {'length': {'maximum': 42.5}}, warnings=warnings)
    assert len(warnings) == 1
    assert warnings[0].path == ["length"]
    assert warnings[0].message == "should be an integer (got float)"

    for minimum, maximum in ((42, 0), (1, 0)):
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'length': {'minimum': minimum, 'maximum': maximum}})
        assert e.value.path == ["length"]
        assert e.value.message == "minimum must be lower than maximum"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'length': {'foo': 'bar'}})
    assert e.value.path == ["length"]
    assert e.value.message == "'foo' property is unexpected"

def option_property_test(specs, path):
    bool_value_property_test(specs, "option", path)

def additional_properties_test(specs):
    errors = []
    validate_specs(specs | {'foo': 'bar', 'bar': 'foo'}, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'bar' property is unexpected"
    assert errors[1].path == []
    assert errors[1].message == "'foo' property is unexpected"

def test_type_block():
    # type blocks must be a dict
    for specs in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs)
        assert e.value.message == "value must be a dict"

    # 'type' property is missing
    missing_property_test({}, 'type')

    # value of 'type' property is incorrect
    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'foo'})
    assert e.value.message == "value of 'type' is incorrect"

def test_flag_type():
    # test minimal specs
    specs = {'type': 'flag'}
    validate_specs(specs)

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test lazy validation
    specs = {
        'type': 'flag',
        'option': 42,
        'foo': 'bar'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["option"]
    assert errors[1].message == "value must be a bool"

def test_number_type():
    # test minimal specs
    specs = {'type': 'number'}
    validate_specs(specs)

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test 'decimal' property
    validate_specs(specs | {'decimal': True})
    validate_specs(specs | {'decimal': False})

    for invalid_value in [42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'decimal': invalid_value})
        assert e.value.path == ["decimal"]
        assert e.value.message == "value must be a bool"

    # test 'minimum' property
    validate_specs(specs | {'minimum': 42})
    validate_specs(specs | {'minimum': {'value': 42}})
    validate_specs(specs | {'minimum': {'exclusive': False, 'value': 42}})
    validate_specs(specs | {'minimum': {'exclusive': True, 'value': 42}})

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'minimum': invalid_value})
        assert e.value.path == ["minimum"]
        assert e.value.message == "value must be either a number or a dict"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'minimum': {'exclusive': False}})
    assert e.value.path == ["minimum"]
    assert e.value.message == "'value' property is missing"

    for invalid_value in [42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'minimum': {'exclusive': invalid_value, 'value': 42}})
        assert e.value.path == ["minimum", "exclusive"]
        assert e.value.message == "value must be a bool"

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'minimum': {'exclusive': False, 'value': invalid_value}})
        assert e.value.path == ["minimum", "value"]
        assert e.value.message == "value must be a number"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'minimum': {'value': 42, 'foo': 'bar'}})
    assert e.value.path == ["minimum"]
    assert e.value.message == "'foo' property is unexpected"

    warnings = []
    validate_specs(specs | {'minimum': {'value': 42.5}}, warnings=warnings)
    assert len(warnings) == 1
    assert warnings[0].path == ["minimum"]
    assert warnings[0].message == "should be an integer (got float)"

    # test 'maximum' property
    validate_specs(specs | {'maximum': 42})
    validate_specs(specs | {'maximum': {'value': 42}})
    validate_specs(specs | {'maximum': {'exclusive': False, 'value': 42}})
    validate_specs(specs | {'maximum': {'exclusive': True, 'value': 42}})

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'maximum': invalid_value})
        assert e.value.path == ["maximum"]
        assert e.value.message == "value must be either a number or a dict"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'maximum': {'exclusive': False}})
    assert e.value.path == ["maximum"]
    assert e.value.message == "'value' property is missing"

    for invalid_value in [42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'maximum': {'exclusive': invalid_value, 'value': 42}})
        assert e.value.path == ["maximum", "exclusive"]
        assert e.value.message == "value must be a bool"

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'maximum': {'exclusive': False, 'value': invalid_value}})
        assert e.value.path == ["maximum", "value"]
        assert e.value.message == "value must be a number"

    with pytest.raises(ValidationError) as e:
        validate_specs(specs | {'maximum': {'value': 42, 'foo': 'bar'}})
    assert e.value.path == ["maximum"]
    assert e.value.message == "'foo' property is unexpected"

    warnings = []
    validate_specs(specs | {'maximum': {'value': 42.5}}, warnings=warnings)
    assert len(warnings) == 1
    assert warnings[0].path == ["maximum"]
    assert warnings[0].message == "should be an integer (got float)"

    # test minimum must be lower than maximum
    for minimum, maximum in ((42, 0), (-9, -10), (1, -1)):
        with pytest.raises(ValidationError) as e:
            validate_specs(specs | {'minimum': minimum, 'maximum': maximum})
        assert e.value.path == []
        assert e.value.message == "minimum must be lower than maximum"

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test lazy validation
    specs = {
        'type': 'number',
        'decimal': 'foo',
        'minimum': False,
        'maximum': "Hello world!",
        'option': 42,
        'foo': 'bar'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["decimal"]
    assert errors[1].message == "value must be a bool"
    assert errors[2].path == ["minimum"]
    assert errors[2].message == "value must be either a number or a dict"
    assert errors[3].path == ["maximum"]
    assert errors[3].message == "value must be either a number or a dict"
    assert errors[4].path == ["option"]
    assert errors[4].message == "value must be a bool"

def test_string_type():
    # test minimal specs
    specs = {'type': 'string'}
    validate_specs(specs)

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'length' property
    length_property_test(specs)

    # test the 'pattern' property
    validate_specs(specs | {'pattern': '^[a-z]+(-[a-z]+)*$'})
    string_value_property_test(specs, 'pattern', [])

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test lazy validation
    specs = {
        'type': 'string',
        'length': False,
        'pattern': 42,
        'option': 42,
        'foo': 'bar'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["length"]
    assert errors[1].message == "value must be either a number or a dict"
    assert errors[2].path == ["pattern"]
    assert errors[2].message == "value must be a string"
    assert errors[3].path == ["option"]
    assert errors[3].message == "value must be a bool"

def test_array_type():
    # test minimal specs
    specs = {
        'type': 'array',
        'value':
            {'type': 'string'
        }
    }

    missing_property_test({'type': 'array'}, 'value')

    validate_specs({'type': 'array', 'value': {'type': 'flag'}})
    validate_specs({'type': 'array', 'value': {'type': 'number'}})
    validate_specs(specs)

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'value' property
    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'array', 'value': {'type': 'foo'}})
    assert e.value.path == ["[]"]
    assert e.value.message == "value of 'type' is incorrect"

    # test the 'length' property
    length_property_test(specs)

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test nested arrays
    nested_arrays = {
        'type': 'array',
        'value': {
            'type': 'array',
            'value': {
                'type': 'array',
                'value': {
                    'type': 'string'
                }
            }
        }
    }
    validate_specs(nested_arrays)

    # test lazy validation
    specs = {
        'type': 'array',
        'value': 42,
        'length': False,
        'option': 42,
        'foo': 'br'
    }


    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["[]"]
    assert errors[1].message == "value must be a dict"
    assert errors[2].path == ["length"]
    assert errors[2].message == "value must be either a number or a dict"
    assert errors[3].path == ["option"]
    assert errors[3].message == "value must be a bool"

def test_object_type():
    # test minimal specs
    specs = {
        'type': 'object',
        'key': 'string',
        'value': {
            'type': 'string'
        }
    }

    missing_property_test(dict_minus_item(specs, 'key'), 'key')
    missing_property_test(dict_minus_item(specs, 'value'), 'value')

    validate_specs(specs)

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'key' property
    for key in ['integer', 'string']:
        validate_specs({'type': 'object', 'key': key, 'value': {'type': 'string'}})

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'object', 'key': 'foo', 'value': {'type': 'string'}})
    assert e.value.path == []
    assert e.value.message == "value of 'key' must be either 'integer' or 'string'"

    # test the 'value' property
    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'object', 'key': 'string', 'value': {'type': 'foo'}})
    assert e.value.path == ["{}"]
    assert e.value.message == "value of 'type' is incorrect"

    # test the 'length' property
    length_property_test(specs)

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test nested objects
    nested_objects = {
        'type': 'object',
        'key': 'integer',
        'value': {
            'type': 'object',
            'key': 'string',
            'value': {
                'type': 'object',
                'key': 'integer',
                'value': {
                    'type': 'string'
                }
            }
        }
    }
    validate_specs(nested_objects)

    # test lazy validation
    specs = {
        'type': 'object',
        'key': 'foo',
        'value': 42,
        'length': False,
        'option': 42,
        'foo': 'br'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["{}"]
    assert errors[1].message == "value must be a dict"
    assert errors[2].path == []
    assert errors[2].message == "value of 'key' must be either 'integer' or 'string'"
    assert errors[3].path == ["length"]
    assert errors[3].message == "value must be either a number or a dict"
    assert errors[4].path == ["option"]
    assert errors[4].message == "value must be a bool"

def test_tuple_type():
    # test minimal specs
    specs = {
        'type': 'tuple',
        'items': [
            {'type': 'flag'},
            {'type': 'number'},
            {'type': 'string'}
        ]
    }

    validate_specs(specs)
    missing_property_test({'type': 'tuple'}, 'items')

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'items' property
    for items in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'tuple', 'items': items})
        assert e.value.path == ["items"]
        assert e.value.message == "value must be a list"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'tuple', 'items': []})
    assert e.value.path == ["items"]
    assert e.value.message == "must contain at least one value"

    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'tuple', 'items': [value]})
        assert e.value.path == ["<0>"]
        assert e.value.message == "value must be a dict"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'tuple', 'items': [{'type': 'foo'}]})
    assert e.value.path == ["<0>"]
    assert e.value.message == "value of 'type' is incorrect"

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test nested tuples
    nested_tuples = {
        'type': 'tuple',
        'items': [
            {
                'type': 'tuple',
                'items': [
                    {
                        'type': 'tuple',
                        'items': [
                            {
                                'type': 'string'
                            }
                        ]
                    }
                ]
            }
        ]
    }
    validate_specs(nested_tuples)

    # test lazy validation
    specs = {
        'type': 'tuple',
        'items': [
            {'type': 'foo'},
            {'type': 'bar'},
            {'type': 'quz'}
        ],
        'option': 42,
        'foo': 'bar'
    }


    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["<0>"]
    assert errors[1].message == "value of 'type' is incorrect"
    assert errors[2].path == ["<1>"]
    assert errors[2].message == "value of 'type' is incorrect"
    assert errors[3].path == ["<2>"]
    assert errors[3].message == "value of 'type' is incorrect"
    assert errors[4].path == ["option"]
    assert errors[4].message == "value must be a bool"

def test_map_type():
    # test minimal specs
    specs = {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'number'},
            'quz': {'type': 'string'}
        }
    }

    validate_specs(specs)
    missing_property_test({'type': 'map'}, 'fields')

    # test 'name' and 'description' properties
    name_property_test(specs)
    description_property_test(specs)

    # test the 'fields' property
    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'map', 'fields': value})
        assert e.value.path == ["fields"]
        assert e.value.message == "value must be a dict"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'map', 'fields': {}})
    assert e.value.path == ["fields"]
    assert e.value.message == "must contain at least one field"

    for name in VALID_NAMES:
        validate_specs({'type': 'map', 'fields': {name: {'type': 'flag'}}})

    for name in INVALID_NAMES:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'map', 'fields': {name: {'type': 'flag'}}})
        assert e.value.path == ["fields"]
        assert e.value.message == f"'{name}' is an incorrect key name"

    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'map', 'fields': {'foo': value}})
        assert e.value.path == ["$foo"]
        assert e.value.message == "value must be a dict"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'map', 'fields': {'foo': {'type': 'bar'}}})
    assert e.value.path == ["$foo"]
    assert e.value.message == "value of 'type' is incorrect"

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test nested maps
    nested_maps = {
        'type': 'map',
        'fields': {
            'foo': {
                'type': 'map',
                'fields': {
                    'bar': {
                        'type': 'map',
                        'fields': {
                            'quz': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
    validate_specs(nested_maps)

    # test lazy validation
    specs = {
        'type': 'map',
        'fields': {
            '-foo': {'type': 'flag'},
            'bar': {'type': 'foo'}
        },
        'option': 42,
        'foo': 'bar'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["fields"]
    assert errors[1].message == "'-foo' is an incorrect key name"
    assert errors[2].path == ["$bar"]
    assert errors[2].message == "value of 'type' is incorrect"
    assert errors[3].path == ["option"]
    assert errors[3].message == "value must be a bool"

def test_enum_type():
    # test minimal specs
    specs = {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz']
    }
    validate_specs(specs)

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'enum'})
    assert e.value.path == []
    assert e.value.message == "'values' property is missing"

    # test 'values' property
    for value in [True, False, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e:
            validate_specs({'type': 'enum', 'values': value})
        assert e.value.path == ["values"]
        assert e.value.message == "value must be a list"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'enum', 'values': []})
    assert e.value.path == ["values"]
    assert e.value.message == "must contain at least one value"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'enum', 'values': ['-foo', 'bar', 'quz']})
    assert e.value.path == ["values"]
    assert e.value.message == "'-foo' is an incorrect value"

    with pytest.raises(ValidationError) as e:
        validate_specs({'type': 'enum', 'values': ['foo', 'bar', 'quz', 'foo']})
    assert e.value.path == ["values"]
    assert e.value.message == "'foo' value is duplicated"

    # test the 'option' property
    option_property_test(specs, [])

    # test additional properties
    additional_properties_test(specs)

    # test lazy validation
    specs = {
        'type': 'enum',
        'values': ['-foo', 'bar', 'quz', 'bar'],
        'option': 42,
        'foo': 'bar'
    }

    errors = []
    validate_specs(specs, errors=errors)

    assert errors[0].path == []
    assert errors[0].message == "'foo' property is unexpected"
    assert errors[1].path == ["values"]
    assert errors[1].message == "'-foo' is an incorrect value"
    assert errors[2].path == ["values"]
    assert errors[2].message == "'bar' value is duplicated"
    assert errors[3].path == ["option"]
    assert errors[3].message == "value must be a bool"
