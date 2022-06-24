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

def validate_minimum_or_maximum_property(name, path, value, errors):
    # This function raises validation error with message "'minimum' property is
    # invalid (whatever)" where 'whatever' is a custom message; it doesn't try
    # to uniformize error messages. It also returns the actual minimal value so
    # the caller can perform further checking easily.

    def raise_error(path, message, errors):
        error = ValidationError(path, f"'{name}' property is invalid ({message})")
        errors.append(error)
        return

    if type(value) in (int, float):
        # If omitted, value is to be understood as not exclusive
        return (False, value)
    elif type(value) is dict:
        # Only 'exclusive' and 'value' properties are accepted.
        extra_properties = set(value.keys()) - {'exclusive', 'value'}
        if extra_properties:
            raise_error(path, f"'{extra_properties.pop()}' property was unexpected", errors)

        exclusive = value.get('exclusive')
        if exclusive and type(exclusive) is not bool:
            raise_error(path, "value of 'exclusive' must be a boolean", errors)
        else:
            exclusive = False

        value_ = value.get('value')
        if value_ == None:
            raise_error(path, "'value' property is missing", errors)
        elif type(value_) not in (int, float):
            raise_error(path, "value of 'value' must be a number", errors)

        return (exclusive, value_)
    else:
        raise_error(path, "must be either a number of a dict", errors)

def validate_length_property(path, value, errors):
    # This function raises validation error with message "'length' property is
    # invalid (whatever)" where 'whatever' is a custom message; it doesn't try
    # to uniformize error messages.

    def raise_error(path, message, errors):
        error = ValidationError(path, f"'length' property is invalid ({message})")
        errors.append(error)
        return

    if type(value) in (int, float):
        if value < 0:
            raise_error(path, "length must be greater or equal to zero", errors)

    elif type(value) is dict:
        # Only 'minimum' and 'maximum' properties are accepted.
        extra_properties = set(value.keys()) - {'minimum', 'maximum'}
        if extra_properties:
            raise_error(path, f"'{extra_properties.pop()}' property was unexpected", errors)

        minimum = value.get('minimum')
        if minimum:
            if type(minimum) not in (int, float):
                raise_error(path, "value of 'minimum' must be a number", errors)
            if minimum < 0:
                raise_error(path, "value of 'length.minimum' must be greater or equal to zero", errors)

        maximum = value.get('maximum')
        if maximum:
            if type(maximum) not in (int, float):
                raise_error(path, "value of 'maximum' must be a number", errors)
            if maximum < 0:
                raise_error(path, "value of 'length.maximum' must be greater or equal to zero", errors)

        if minimum != None and maximum != None:
            if minimum > maximum:
                raise_error(path, "length.maximum must be greater than length.minimum", errors)

def validate_option_property(path, block, errors, warnings):
    if 'option' in block and type(block['option']) is not bool:
        error = ValidationError(path, "value of 'option' must be a boolean")
        errors.append(error)
        return

def validate_flag_type(path, block, errors, warnings):
    # TODO; Code related to 'default' is disabled temporarily.
    # if 'default' in block and type(block['default']) is not bool:
    #     error = ValidationError(path, "value of 'default' must be a boolean")
    #     errors.append(error)
    #     return
    pass

def validate_integer_type(path, block, errors, warnings):
    minimum = None
    if 'minimum' in block:
        minimum = validate_minimum_or_maximum_property('minimum', path, block['minimum'], errors)

    maximum = None
    if 'maximum' in block:
        maximum = validate_minimum_or_maximum_property('maximum', path, block['maximum'], errors)

    if minimum and maximum:
        if maximum[1] < minimum[1]:
            error = ValidationError(path, "maximum must be lower than minimum")
            errors.append(error)
            return

    # TODO; Code related to 'default' is disabled temporarily.
    # if 'default' in block and type(block['default']) not in (int, float):
    #     error = ValidationError(path, "value of 'default' must be a number")
    #     errors.append(error)
    #     return

def validate_decimal_type(path, block, errors, warnings):
    # TODO; To be implemented.
    pass

    # TODO; Code related to 'default' is disabled temporarily.
    # if 'default' in block and type(block['default']) not in (int, float):
    #     error = ValidationError(path, "value of 'default' must be a number")
    #     errors.append(error)
    #     return

def validate_string_type(path, block, errors, warnings):
    if 'length' in block:
        validate_length_property(path, block['length'], errors)

    pattern = block.get('pattern')
    if pattern != None:
        if type(pattern) is not str:
            error = ValidationError(path, "value of 'pattern' must be a string")
            errors.append(error)
            return

    # TODO; Code related to 'default' is disabled temporarily.
    # if 'default' in block and type(block['default']) is not str:
    #     error = ValidationError(path, "value of 'default' must be a number")
    #     errors.append(error)
    #     return

def validate_enum_type(path, block, errors, warnings):
    pass

def validate_list_type(path, block, errors, warnings):
    value = block.get('value')
    if not value:
        error = ValidationError(path, "'value' property is missing")
        errors.append(error)
        return

    validate_value_type(path + '.[]', value, errors, warnings)

    if 'length' in block:
        validate_length_property(path, block['length'], errors)

def validate_tuple_type(path, block, errors, warnings):
    values = block.get('values')
    if values == None:
        error = ValidationError(path, "'values' property is missing")
        errors.append(error)
        return

    if type(values) is not list:
        error = ValidationError(path, "value of 'values' must be a list")
        errors.append(error)
        return

    if len(values) == 0:
        error = ValidationError(path, "must contain at least one value")
        errors.append(error)
        return

    for (index, value) in enumerate(values):
        validate_value_type(path + '.{' + str(index) + '}', value, errors, warnings)

def validate_map_type(path, block, errors, warnings):
    fields = block.get("fields")
    if fields == None:
        error = ValidationError(path, "'fields' property is missing")
        errors.append(error)
        return

    if type(fields) is not dict:
        error = ValidationError(path, "'fields' property must be a dict")
        errors.append(error)
        return

    if len(fields) == 0:
        error = ValidationError(path, "must contain at least one field")
        errors.append(error)
        return

    for key in fields.keys():
        if not re.match(r"^[a-z]+(-[a-z]+)*$", key):
            error = ValidationError(path, "'fields' has incorrect key name")
            errors.append(error)
            return

    for key, value in fields.items():
        validate_value_type(path + "." + key, value, errors, warnings)

validators = {
    "flag"     : (validate_flag_type,     []),
    "integer"  : (validate_integer_type,  ['minimum', 'maximum']),
    "decimal"  : (validate_decimal_type,  ['minimum', 'maximum']),
    "string"   : (validate_string_type,   ['length', 'pattern']),
    "enum"     : (validate_enum_type,     ['values']),
    "list"     : (validate_list_type,     ['value', 'length']),
    "tuple"    : (validate_tuple_type,    ['values']),
    "map"      : (validate_map_type,      ['fields'])
}

def validate_value_type(path, block, errors, warnings):
    if type(block) is not dict:
        error = ValidationError(path, "value must be a dict")
        errors.append(error)
        return

    type_ = block.get("type")
    if not type_:
        error = ValidationError(path, "'type' property is missing")
        errors.append(error)
        return

    if type_ not in validators.keys():
        error = ValidationError(path, "value of 'type' is incorrect")
        errors.append(error)
        return

    extra_properties = set(block.keys()) - set(validators[type_][1]) - {'type', 'option'}
    if extra_properties:
        error = ValidationError(path, f"'{extra_properties.pop()}' property was unexpected")
        errors.append(error)
        return

    validators[type_][0](path, block, errors, warnings)

    validate_option_property(path, block, errors, warnings)

def validate_root_block(block, errors, warnings):
    if type(block) is not dict:
        # Early termination if the root block is not a dict.
        error = ValidationError("root", "root element must be a dict")
        errors.append(error)
        return

    validate_value_type("root", block, errors, warnings)

def validate_specs(specs, errors=None, warnings=None):
    """ Validate the YAML specs.

    This function checks if the structure of the YAML specs is correct. If not,
    the ValidatorError exception is raised.
    """

    assert errors is None or errors == [], "if the errors parameter is set, it must be an empty list"
    assert warnings is None or warnings == [], "if the warnings parameter is set, it must be an empty list"

    # We detect if users want lazy validation when they pass an empty list as
    # the errors parameters.
    lazy_validation = False
    if errors is None:
        errors = []
    else:
        lazy_validation = True

    if warnings is None:
        warnings = []

    validate_root_block(specs, errors, warnings)

    # If we're not lazy-validating the specs, we raise the first error that
    # occurred.
    if not lazy_validation and len(errors) > 0:
        raise errors[0]
