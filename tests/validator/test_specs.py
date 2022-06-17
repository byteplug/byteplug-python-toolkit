# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.validator import validate_specs
from byteplug.validator import ValidationError
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

def bool_value_property_test(specs, key):
    validate_specs(specs | {key: True})
    validate_specs(specs | {key: False})

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: 42})
    assert e_info.value.message == f"value of '{key}' must be a boolean"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: "Hello world!"})
    assert e_info.value.message == f"value of '{key}' must be a boolean"

def number_value_property_test(specs, key):
    validate_specs(specs | {key: 42})

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: False})
    assert e_info.value.message == f"value of '{key}' must be a number"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: True})
    assert e_info.value.message == f"value of '{key}' must be a number"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: "Hello world!"})
    assert e_info.value.message == f"value of '{key}' must be a number"

def string_value_property_test(specs, key):
    validate_specs(specs | {key: "Hello world!"})

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: False})
    assert e_info.value.message == f"value of '{key}' must be a string"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: True})
    assert e_info.value.message == f"value of '{key}' must be a string"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {key: 42})
    assert e_info.value.message == f"value of '{key}' must be a string"

def option_property_test(specs):
    bool_value_property_test(specs, "option")

def additional_properties_test(specs):
    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'foo': 'bar'})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'foo' property was unexpected"

def test_root_block():
    # root block must be a dict
    for specs in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs)
        assert e_info.value.message == "root element must be a dict"

    # 'type' property is missing
    with pytest.raises(ValidationError) as e_info:
        validate_specs({})
    assert e_info.value.message == "'type' property is missing"

    # value of 'type' property is incorrect
    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'foo'})
    assert e_info.value.message == "value of 'type' is incorrect"

def test_flag_type():
    # test minimal specs
    specs = {'type': 'flag'}
    validate_specs(specs)

    # test the 'default' property
    bool_value_property_test(specs, 'default')

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

def test_integer_type():
    # test minimal specs
    specs = {'type': 'integer'}
    validate_specs(specs)

    # test 'minimum' property
    validate_specs(specs | {'minimum': 42})
    validate_specs(specs | {'minimum': {'value': 42}})
    validate_specs(specs | {'minimum': {'exclusive': False, 'value': 42}})
    validate_specs(specs | {'minimum': {'exclusive': True, 'value': 42}})

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'minimum': invalid_value})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'minimum' property is invalid (must be either a number of a dict)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'minimum': {'exclusive': False}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'minimum' property is invalid ('value' property is missing)"

    for invalid_value in [42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'minimum': {'exclusive': invalid_value, 'value': 42}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'minimum' property is invalid (value of 'exclusive' must be a boolean)"

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'minimum': {'exclusive': False, 'value': invalid_value}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'minimum' property is invalid (value of 'value' must be a number)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'minimum': {'value': 42, 'foo': 'bar'}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'minimum' property is invalid ('foo' property was unexpected)"

    # test 'maximum' property
    validate_specs(specs | {'maximum': 42})
    validate_specs(specs | {'maximum': {'value': 42}})
    validate_specs(specs | {'maximum': {'exclusive': False, 'value': 42}})
    validate_specs(specs | {'maximum': {'exclusive': True, 'value': 42}})

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'maximum': invalid_value})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'maximum' property is invalid (must be either a number of a dict)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'maximum': {'exclusive': False}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'maximum' property is invalid ('value' property is missing)"

    for invalid_value in [42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'maximum': {'exclusive': invalid_value, 'value': 42}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'maximum' property is invalid (value of 'exclusive' must be a boolean)"

    for invalid_value in [False, True, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'maximum': {'exclusive': False, 'value': invalid_value}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'maximum' property is invalid (value of 'value' must be a number)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'maximum': {'value': 42, 'foo': 'bar'}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'maximum' property is invalid ('foo' property was unexpected)"

    # test maximum must be higher than minimum
    for minimum, maximum in ((42, 0), (-9, -10), (1, -1)):
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'minimum': minimum, 'maximum': maximum})
        assert e_info.value.path == "root"
        assert e_info.value.message == "maximum must be lower than minimum"

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

def test_decimal_type():
    # test minimal specs
    specs = {'type': 'decimal'}
    validate_specs(specs)

    # test 'foo'
    pass

    # test 'bar'
    pass

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

def test_string_type():
    # test minimal specs
    specs = {'type': 'string'}
    validate_specs(specs)

    # test the 'length' property
    validate_specs(specs | {'length': 42})

    validate_specs(specs | {'length': {'minimum': 42}})
    validate_specs(specs | {'length': {'maximum': 42}})
    validate_specs(specs | {'length': {'minimum': 0, 'maximum': 42}})

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': -1})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (length must be greater or equal to zero)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'minimum': -1}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (value of 'length.minimum' must be greater or equal to zero)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'maximum': -1}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (value of 'length.maximum' must be greater or equal to zero)"

    for minimum, maximum in ((42, 0), (1, 0)):
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'length': {'minimum': minimum, 'maximum': maximum}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'length' property is invalid (length.maximum must be greater than length.minimum)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'foo': 'bar'}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid ('foo' property was unexpected)"

    # test the 'pattern' property
    validate_specs(specs | {'pattern': '^[a-z]+(-[a-z]+)*$'})
    string_value_property_test(specs, 'pattern')

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

def test_enum_type():
    # test minimal specs
    specs = {'type': 'enum'}
    validate_specs(specs)

    # test 'foo'
    pass

    # test 'bar'
    pass

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

def test_list_type():
    # test minimal specs
    specs = {'type': 'list', 'value': {'type': 'string'}}

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'list'})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'value' property is missing"

    validate_specs({'type': 'list', 'value': {'type': 'flag'}})
    validate_specs({'type': 'list', 'value': {'type': 'integer'}})
    validate_specs(specs)

    # test the 'value' property
    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'list', 'value': {'type': 'foo'}})
    assert e_info.value.path == "root.[]"
    assert e_info.value.message == "value of 'type' is incorrect"

    # test the 'length' property
    validate_specs(specs | {'length': 42})

    validate_specs(specs | {'length': {'minimum': 42}})
    validate_specs(specs | {'length': {'maximum': 42}})
    validate_specs(specs | {'length': {'minimum': 0, 'maximum': 42}})

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': -1})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (length must be greater or equal to zero)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'minimum': -1}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (value of 'length.minimum' must be greater or equal to zero)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'maximum': -1}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid (value of 'length.maximum' must be greater or equal to zero)"

    for minimum, maximum in ((42, 0), (1, 0)):
        with pytest.raises(ValidationError) as e_info:
            validate_specs(specs | {'length': {'minimum': minimum, 'maximum': maximum}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'length' property is invalid (length.maximum must be greater than length.minimum)"

    with pytest.raises(ValidationError) as e_info:
        validate_specs(specs | {'length': {'foo': 'bar'}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'length' property is invalid ('foo' property was unexpected)"

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

    # test nested lists
    nested_lists = {
        'type': 'list',
        'value': {
            'type': 'list',
            'value': {
                'type': 'list',
                'value': {
                    'type': 'string'
                }
            }
        }
    }
    validate_specs(nested_lists)

def test_tuple_type():
    # test minimal specs
    specs = {
        'type': 'tuple',
        'values': [
            {'type': 'flag'},
            {'type': 'integer'},
            {'type': 'string'}
        ]
    }

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'tuple'})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'values' property is missing"

    validate_specs(specs)

    # test the 'values' property
    for values in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs({'type': 'tuple', 'values': values})
        assert e_info.value.path == "root"
        assert e_info.value.message == "value of 'values' must be a list"

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'tuple', 'values': []})
    assert e_info.value.path == "root"
    assert e_info.value.message == "must contain at least one value"

    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs({'type': 'tuple', 'values': [value]})
        assert e_info.value.path == "root.{0}"
        assert e_info.value.message == "value must be a dict"

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'tuple', 'values': [{'type': 'foo'}]})
    assert e_info.value.path == "root.{0}"
    assert e_info.value.message == "value of 'type' is incorrect"

    # test the 'option' property
    option_property_test(specs)

    # test additional properties
    additional_properties_test(specs)

    # test nested tuples
    nested_tuples = {
        'type': 'tuple',
        'values': [
            {
                'type': 'tuple',
                'values': [
                    {
                        'type': 'tuple',
                        'values': [
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

def test_map_type():
    # test minimal specs
    specs = {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'integer'},
            'quz': {'type': 'string'}
        }
    }

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'map'})
    assert e_info.value.path == "root"
    assert e_info.value.message == "'fields' property is missing"

    validate_specs(specs)

    # test the 'fields' property
    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs({'type': 'map', 'fields': value})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'fields' property must be a dict"

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'map', 'fields': {}})
    assert e_info.value.path == "root"
    assert e_info.value.message == "must contain at least one field"

    for name in VALID_NAMES:
        validate_specs({'type': 'map', 'fields': {name: {'type': 'flag'}}})

    for name in INVALID_NAMES:
        with pytest.raises(ValidationError) as e_info:
            validate_specs({'type': 'map', 'fields': {name: {'type': 'flag'}}})
        assert e_info.value.path == "root"
        assert e_info.value.message == "'fields' has incorrect key name"

    for value in [False, True, 42, "Hello world!"]:
        with pytest.raises(ValidationError) as e_info:
            validate_specs({'type': 'map', 'fields': {'foo': value}})
        assert e_info.value.path == "root.foo"
        assert e_info.value.message == "value must be a dict"

    with pytest.raises(ValidationError) as e_info:
        validate_specs({'type': 'map', 'fields': {'foo': {'type': 'bar'}}})
    assert e_info.value.path == "root.foo"
    assert e_info.value.message == "value of 'type' is incorrect"

    # test the 'option' property
    option_property_test(specs)

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
