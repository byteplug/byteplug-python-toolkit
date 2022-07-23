# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
from byteplug.document.exception import ValidationError, ValidationWarning

__all__ = ['validate_specs']

# TODOs;
# - Rework the entire implementation to be based on another generic validator
#   module ?
# - Parse directly YAML files in order to preserve lines and columns infos and
#   emit more precise error/warning messages. Will also be faster.
#

def validate_minimum_or_maximum_property(name, path, value, errors):
    # This function also returns the actual minimal (or maximum) value so the
    # caller can perform further checking easily.

    if type(value) in (int, float):
        # If omitted, value is to be understood as not exclusive.
        return (False, value)
    elif type(value) is dict:
        # Only 'exclusive' and 'value' properties are accepted.
        extra_properties = set(value.keys()) - {'exclusive', 'value'}
        if extra_properties:
            error = ValidationError(path + f'.{name}', f"'{extra_properties.pop()}' property is unexpected")
            errors.append(error)
            return

        exclusive = value.get('exclusive')
        if exclusive and type(exclusive) is not bool:
            error = ValidationError(path + f'.{name}.exclusive', f"value must be a bool")
            errors.append(error)
        else:
            exclusive = False

        value_ = value.get('value')
        if value_ == None:
            error = ValidationError(path + f'.{name}', "'value' property is missing")
            errors.append(error)
        elif type(value_) not in (int, float):
            error = ValidationError(path + f'.{name}.value', "value must be a number")
            errors.append(error)

        return (exclusive, value_)
    else:
        error = ValidationError(path + f'.{name}', f"value must be either a number or a dict")
        errors.append(error)

def validate_length_property(path, value, errors, warnings):

    path = path + '.length'

    if type(value) in (int, float):
        if value < 0:
            error = ValidationError(path, "must be greater or equal to zero")
            errors.append(error)

        if type(value) is float:
            warning = ValidationWarning(path, "should be an integer (got float)")
            warnings.append(warning)

    elif type(value) is dict:
        # Only 'minimum' and 'maximum' properties are accepted.
        extra_properties = set(value.keys()) - {'minimum', 'maximum'}
        if extra_properties:
            error = ValidationError(path, f"'{extra_properties.pop()}' property is unexpected")
            errors.append(error)
            return

        minimum = value.get('minimum')
        if minimum:
            if type(minimum) not in (int, float):
                error = ValidationError(path + '.minimum', "value must be a number")
                errors.append(error)

            if type(minimum) is float:
                warning = ValidationWarning(path, "should be an integer (got float)")
                warnings.append(warning)

            if minimum < 0:
                error = ValidationError(path + '.minimum', "must be greater or equal to zero")
                errors.append(error)

        maximum = value.get('maximum')
        if maximum:
            if type(maximum) not in (int, float):
                error = ValidationError(path + '.maximum', "value must be a number")
                errors.append(error)

            if type(maximum) is float:
                warning = ValidationWarning(path, "should be an integer (got float)")
                warnings.append(warning)

            if maximum < 0:
                error = ValidationError(path + '.maximum', "must be greater or equal to zero")
                errors.append(error)

        if minimum != None and maximum != None:
            if minimum > maximum:
                error = ValidationError(path, "minimum must be lower than maximum")
                errors.append(error)
    else:
        error = ValidationError(path, "value must be either a number or a dict")
        errors.append(error)

def validate_flag_type(path, block, errors, warnings):
    # Nothing to do.
    pass

def validate_integer_type(path, block, errors, warnings):
    minimum = None
    if 'minimum' in block:
        minimum = validate_minimum_or_maximum_property('minimum', path, block['minimum'], errors)

        # TODO; The path is not accurate, it should either be .minimum.value or .minimum
        if minimum is not None and type(minimum[1]) is float:
            warning = ValidationWarning(path + '.minimum', "should be an integer (got float)")
            warnings.append(warning)

    maximum = None
    if 'maximum' in block:
        maximum = validate_minimum_or_maximum_property('maximum', path, block['maximum'], errors)

        # TODO; The path is not accurate, it should either be .maximum.value or .maximum
        if maximum is not None and type(maximum[1]) is float:
            warning = ValidationWarning(path + '.maximum', "should be an integer (got float)")
            warnings.append(warning)

    if minimum and maximum:
        if maximum[1] < minimum[1]:
            error = ValidationError(path, "minimum must be lower than maximum")
            errors.append(error)

def validate_decimal_type(path, block, errors, warnings):
    minimum = None
    if 'minimum' in block:
        minimum = validate_minimum_or_maximum_property('minimum', path, block['minimum'], errors)

    maximum = None
    if 'maximum' in block:
        maximum = validate_minimum_or_maximum_property('maximum', path, block['maximum'], errors)

    if minimum and maximum:
        if maximum[1] < minimum[1]:
            error = ValidationError(path, "minimum must be lower than maximum")
            errors.append(error)

def validate_string_type(path, block, errors, warnings):
    if 'length' in block:
        validate_length_property(path, block['length'], errors, warnings)

    # TODO; Check validity of the regex.
    pattern = block.get('pattern')
    if pattern != None:
        if type(pattern) is not str:
            error = ValidationError(path + '.pattern', "value must be a string")
            errors.append(error)

def validate_enum_type(path, block, errors, warnings):
    values = block.get('values')
    if values is None:
        error = ValidationError(path, "'values' property is missing")
        errors.append(error)
        return

    if type(values) is not list:
        error = ValidationError(path + '.values', "value must be a list")
        errors.append(error)
        return

    if len(values) == 0:
        error = ValidationError(path + '.values', "must contain at least one value")
        errors.append(error)
        return

    # Check for duplicates and check for validity of their value.
    processed_values = []
    for value in values:
        if not re.match(r"^[a-z]+(-[a-z]+)*$", value):
            error = ValidationError(path + '.values', f"'{value}' is an incorrect value")
            errors.append(error)
            continue

        if value in processed_values:
            error = ValidationError(path + '.values', f"'{value}' value is duplicated")
            errors.append(error)
            continue
        else:
            processed_values.append(value)

def validate_list_type(path, block, errors, warnings):
    value = block.get('value')
    if not value:
        error = ValidationError(path, "'value' property is missing")
        errors.append(error)
        return

    validate_block(path + '.[]', value, errors, warnings)

    if 'length' in block:
        validate_length_property(path, block['length'], errors, warnings)

def validate_tuple_type(path, block, errors, warnings):
    values = block.get('values')
    if values == None:
        error = ValidationError(path, "'values' property is missing")
        errors.append(error)
        return

    if type(values) is not list:
        error = ValidationError(path + '.values', "value must be a list")
        errors.append(error)
        return

    if len(values) == 0:
        error = ValidationError(path + '.values', "must contain at least one value")
        errors.append(error)
        return

    for (index, value) in enumerate(values):
        validate_block(path + '.(' + str(index) + ')', value, errors, warnings)

def validate_map_type(path, block, errors, warnings):
    fields = block.get("fields")
    if fields == None:
        error = ValidationError(path, "'fields' property is missing")
        errors.append(error)
        return

    if type(fields) is not dict:
        error = ValidationError(path + '.fields', "value must be a dict")
        errors.append(error)
        return

    if len(fields) == 0:
        error = ValidationError(path + '.fields', "must contain at least one field")
        errors.append(error)
        return

    for key, value in fields.items():
        if not re.match(r"^[a-z]+(-[a-z]+)*$", key):
            error = ValidationError(path + '.fields', f"'{key}' is an incorrect key name")
            errors.append(error)
            continue

        validate_block(path + "." + key, value, errors, warnings)

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

def validate_block(path, block, errors, warnings):
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
        error = ValidationError(path, f"'{extra_properties.pop()}' property is unexpected")
        errors.append(error)

    validators[type_][0](path, block, errors, warnings)

    if 'option' in block and type(block['option']) is not bool:
        error = ValidationError(path + '.option', "value must be a bool")
        errors.append(error)

def validate_root_block(block, errors, warnings):
    if type(block) is not dict:
        # Early termination if the root block is not a dict.
        error = ValidationError("root", "root value must be a dict")
        errors.append(error)
        return

    validate_block("root", block, errors, warnings)

def validate_specs(specs, errors=None, warnings=None):
    """ Validate the YAML specs.

    This function checks if the structure of the YAML specs is correct. If not,
    the ValidatorError exception is raised.

    Possible error messages.

    - root value must be a dict
    - value of 'type' is incorrect
    - value must be a bool|int|float|number|str|list|tuple|dict
    - value must be either a number or a dict
    - '<foo>' property is missing
    - '<foo>' property is unexpected
    - value must be greater or equal to zero
    - minimum must be lower than maximum
    - length must be greater or equal to zero
    - must contain at least one value
    - '<foo>' is an incorrect value
    - '<foo>' value is duplicated
    - must contain at least one field
    - '<foo>' is an incorrect key name

    Possible warning messages.

    - should be an integer (got float)

    When validating the length property and when validating the minimum and
    maximum property for integers.
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
