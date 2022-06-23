# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
from byteplug.validator.exception import ValidationError

__all__ = ['validate_specs']

def validate_minimum_or_maximum_property(name, path, value):
    # This function raises validation error with message "'minimum' property is
    # invalid (whatever)" where 'whatever' is a custom message; it doesn't try
    # to uniformize error messages. It also returns the actual minimal value so
    # the caller can perform further checking easily.

    def raise_error(path, message):
        raise ValidationError(path, f"'{name}' property is invalid ({message})")

    if type(value) in (int, float):
        # If omitted, value is to be understood as not exclusive
        return (False, value)
    elif type(value) is dict:
        # Only 'exclusive' and 'value' properties are accepted.
        extra_properties = set(value.keys()) - {'exclusive', 'value'}
        if extra_properties:
            raise_error(path, f"'{extra_properties.pop()}' property was unexpected")

        exclusive = value.get('exclusive')
        if exclusive and type(exclusive) is not bool:
            raise_error(path, "value of 'exclusive' must be a boolean")
        else:
            exclusive = False

        value_ = value.get('value')
        if value_ == None:
            raise_error(path, "'value' property is missing")
        elif type(value_) not in (int, float):
            raise_error(path, "value of 'value' must be a number")

        return (exclusive, value_)
    else:
        raise_error(path, "must be either a number of a dict")

def validate_length_property(path, value):
    # This function raises validation error with message "'length' property is
    # invalid (whatever)" where 'whatever' is a custom message; it doesn't try
    # to uniformize error messages.

    def raise_error(path, message):
        raise ValidationError(path, f"'length' property is invalid ({message})")

    if type(value) in (int, float):
        if value < 0:
            raise_error(path, "length must be greater or equal to zero")

    elif type(value) is dict:
        # Only 'minimum' and 'maximum' properties are accepted.
        extra_properties = set(value.keys()) - {'minimum', 'maximum'}
        if extra_properties:
            raise_error(path, f"'{extra_properties.pop()}' property was unexpected")

        minimum = value.get('minimum')
        if minimum:
            if type(minimum) not in (int, float):
                raise_error(path, "value of 'minimum' must be a number")
            if minimum < 0:
                raise_error(path, "value of 'length.minimum' must be greater or equal to zero")

        maximum = value.get('maximum')
        if maximum:
            if type(maximum) not in (int, float):
                raise_error(path, "value of 'maximum' must be a number")
            if maximum < 0:
                raise_error(path, "value of 'length.maximum' must be greater or equal to zero")

        if minimum != None and maximum != None:
            if minimum > maximum:
                raise_error(path, "length.maximum must be greater than length.minimum")

def validate_option_property(path, block):
    if 'option' in block and type(block['option']) is not bool:
        raise ValidationError(path, "value of 'option' must be a boolean")

def validate_flag_type(path, block):
    if 'default' in block and type(block['default']) is not bool:
        raise ValidationError(path, "value of 'default' must be a boolean")

def validate_integer_type(path, block):
    minimum = None
    if 'minimum' in block:
        minimum = validate_minimum_or_maximum_property('minimum', path, block['minimum'])

    maximum = None
    if 'maximum' in block:
        maximum = validate_minimum_or_maximum_property('maximum', path, block['maximum'])

    if minimum and maximum:
        if maximum[1] < minimum[1]:
            raise ValidationError(path, "maximum must be lower than minimum")

    if 'default' in block and type(block['default']) not in (int, float):
        raise ValidationError(path, "value of 'default' must be a number")

def validate_decimal_type(path, block):
    # TODO; To be implemented.
    if 'default' in block and type(block['default']) not in (int, float):
        raise ValidationError(path, "value of 'default' must be a number")

def validate_string_type(path, block):
    if 'length' in block:
        validate_length_property(path, block['length'])

    pattern = block.get('pattern')
    if pattern != None:
        if type(pattern) is not str:
            raise ValidationError(path, "value of 'pattern' must be a string")

    if 'default' in block and type(block['default']) is not str:
        raise ValidationError(path, "value of 'default' must be a number")

def validate_enum_type(path, block):
    pass

def validate_list_type(path, block):
    value = block.get('value')
    if not value:
        raise ValidationError(path, "'value' property is missing")

    validate_value_type(path + '.[]', value)

    if 'length' in block:
        validate_length_property(path, block['length'])

def validate_tuple_type(path, block):
    values = block.get('values')
    if values == None:
        raise ValidationError(path, "'values' property is missing")

    if type(values) is not list:
        raise ValidationError(path, "value of 'values' must be a list")

    if len(values) == 0:
        raise ValidationError(path, "must contain at least one value")

    for (index, value) in enumerate(values):
        validate_value_type(path + '.{' + str(index) + '}', value)

def validate_map_type(path, block):
    fields = block.get("fields")
    if fields == None:
        raise ValidationError(path, "'fields' property is missing")

    if type(fields) is not dict:
        raise ValidationError(path, "'fields' property must be a dict")

    if len(fields) == 0:
        raise ValidationError(path, "must contain at least one field")

    for key in fields.keys():
        if not re.match(r"^[a-z]+(-[a-z]+)*$", key):
            raise ValidationError(path, "'fields' has incorrect key name")

    for key, value in fields.items():
        validate_value_type(path + "." + key, value)

validators = {
    "flag"     : (validate_flag_type,     ['default']),
    "integer"  : (validate_integer_type,  ['minimum', 'maximum', 'default']),
    "decimal"  : (validate_decimal_type,  ['minimum', 'maximum', 'default']),
    "string"   : (validate_string_type,   ['length', 'pattern']),
    "enum"     : (validate_enum_type,     ['values', 'default']),
    "list"     : (validate_list_type,     ['value', 'length']),
    "tuple"    : (validate_tuple_type,    ['values']),
    "map"      : (validate_map_type,      ['fields'])
}

def validate_value_type(path, block):
    if type(block) is not dict:
        raise ValidationError(path, "value must be a dict")

    type_ = block.get("type")
    if not type_:
        raise ValidationError(path, "'type' property is missing")

    if type_ not in validators.keys():
        raise ValidationError(path, "value of 'type' is incorrect")

    extra_properties = set(block.keys()) - set(validators[type_][1]) - {'type', 'option'}
    if extra_properties:
        raise ValidationError(path, f"'{extra_properties.pop()}' property was unexpected")

    validators[type_][0](path, block)

    validate_option_property(path, block)

def validate_specs(specs):
    """ Validate the YAML specs.

    This function checks if the structure of the YAML specs is correct. If not,
    the ValidatorError exception is raised.
    """

    if type(specs) is not dict:
        raise ValidationError("root", "root element must be a dict")

    validate_value_type("root", specs)

def json_to_object(json, specs):
    pass

def object_to_json(object, specs):
    pass
