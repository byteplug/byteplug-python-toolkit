# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
import json
from byteplug.document.utils import read_minimum_value, read_maximum_value
from byteplug.document.exception import ValidationError

# Notes:
# - This module handles validation and conversion from Python object to JSON
#   document. It must be kept in sync with the 'document' module.
# - In all process_<type>_node(), it's about converting and adjusting a Python
#   node/value so it gets converted to the right JSON type later (see the
#   'json' module).
# - For each node type, we refer to the standard document that describes how
#   the augmented type is implemented in its JSON form; we care about validity
#   of its JSON form, its Python form is not defined by the standard.

__all__ = ['object_to_document']

def process_flag_node(path, node, specs, errors, warnings):
    if type(node) is not bool:
        error = ValidationError(path, "was expecting a boolean")
        errors.append(error)
        return

    return node

def process_integer_node(path, node, specs, errors, warnings):
    if type(node) is not int:
        error = ValidationError(path, "was expecting an integer")
        errors.append(error)
        return

    node_errors = []

    minimum = read_minimum_value(specs)
    maximum = read_maximum_value(specs)

    if minimum:
        is_exclusive, value = minimum
        value = int(value)

        if is_exclusive:
            if not (node > value):
                error = ValidationError(path, f"value must be strictly greater than {value}")
                node_errors.append(error)
        else:
            if not (node >= value):
                error = ValidationError(path, f"value must be equal or greater than {value}")
                node_errors.append(error)

    if maximum:
        is_exclusive, value = maximum
        value = int(value)

        if is_exclusive:
            if not (node < value):
                error = ValidationError(path, f"value must be strictly lower than {value}")
                node_errors.append(error)
        else:
            if not (node <= value):
                error = ValidationError(path, f"value must be equal or lower than {value}")
                node_errors.append(error)

    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return node

def process_string_node(path, node, specs, errors, warnings):
    if type(node) is not str:
        error = ValidationError(path, "was expecting a string")
        errors.append(error)
        return

    node_errors = []

    length = specs.get('length')
    if length is not None:
        if type(length) in (int, float):
            length = int(length)

            if len(node) != length:
                error = ValidationError(path, f"length must be equal to {length}")
                node_errors.append(error)
        else:
            minimum = length.get("minimum")
            maximum = length.get("maximum")

            if minimum is not None:
                minimum = int(minimum)

                if not (len(node) >= minimum):
                    error = ValidationError(path, f"length must be equal or greater than {minimum}")
                    node_errors.append(error)

            if maximum is not None:
                maximum = int(maximum)

                if not (len(node) <= maximum):
                    error = ValidationError(path, f"length must be equal or lower than {maximum}")
                    node_errors.append(error)

    pattern = specs.get('pattern')
    if pattern is not None:
        if not re.match(pattern, node):
            error = ValidationError(path, "value did not match the pattern")
            node_errors.append(error)

    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return node

def process_list_node(path, node, specs, errors, warnings):
    value = specs['value']

    if type(node) is not list:
        error = ValidationError(path, "was expecting a list")
        errors.append(error)
        return

    length = specs.get('length')
    if length is not None:
        if type(length) in (int, float):
            length = int(length)

            if len(node) != length:
                error = ValidationError(path, f"length must be equal to {length}")
                errors.append(error)
                return
        else:
            minimum = length.get("minimum")
            maximum = length.get("maximum")

            if minimum is not None:
                minimum = int(minimum)

                if not (len(node) >= minimum):
                    error = ValidationError(path, f"length must be equal or greater than {minimum}")
                    errors.append(error)
                    return

            if maximum is not None:
                maximum = int(maximum)

                if not (len(node) <= maximum):
                    error = ValidationError(path, f"length must be equal or lower than {maximum}")
                    errors.append(error)
                    return

    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_item = adjust_node(path + ['[' + str(index) + ']'], item, value, errors, warnings)
        adjusted_node.append(adjusted_item)

    return adjusted_node

def process_tuple_node(path, node, specs, errors, warnings):
    values = specs['values']

    if type(node) is not tuple:
        error = ValidationError(path, "was expecting a tuple")
        errors.append(error)
        return

    if len(node) != len(values):
        error = ValidationError(path, f"length of the tuple must be {len(values)}")
        errors.append(error)
        return

    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_item = adjust_node(path + ['(' + str(index) + ')'], item, values[index], errors, warnings)
        adjusted_node.append(adjusted_item)

    return adjusted_node

def process_map_node(path, node, specs, errors, warnings):
    fields = specs['fields']

    if type(node) is not dict:
        error = ValidationError(path, "was expecting a dict")
        errors.append(error)
        return

    for key in node.keys():
        if type(key) is not str:
            error = ValidationError(path, "keys of the dict must be string exclusively")
            errors.append(error)
            return

    node_errors = []

    adjusted_node = {}
    for key, value in node.items():
        if key in fields.keys():
            adjusted_node[key] = adjust_node(path + ['{' + key + '}'], value, fields[key], errors, warnings)
        else:
            error = ValidationError(path, f"'{key}' field was unexpected")
            errors.append(error)

    missing_keys = set(fields.keys()) - set(adjusted_node.keys())
    for key in missing_keys:
        error = ValidationError(path, f"'{key}' field was missing")
        errors.append(error)

    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return adjusted_node

def process_decimal_node(path, node, specs, errors, warnings):
    if type(node) is not float:
        error = ValidationError(path, "was expecting a float")
        errors.append(error)
        return

    node_errors = []

    minimum = read_minimum_value(specs)
    maximum = read_maximum_value(specs)

    if minimum:
        is_exclusive, value = minimum
        if is_exclusive:
            if not (node > value):
                error = ValidationError(path, f"value must be strictly greater than {value}")
                node_errors.append(error)
        else:
            if not (node >= value):
                error = ValidationError(path, f"value must be equal or greater than {value}")
                node_errors.append(error)

    if maximum:
        is_exclusive, value = maximum
        if is_exclusive:
            if not (node < value):
                error = ValidationError(path, f"value must be strictly lower than {value}")
                node_errors.append(error)
        else:
            if not (node <= value):
                error = ValidationError(path, f"value must be equal or lower than {value}")
                node_errors.append(error)

    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return node

def process_enum_node(path, node, specs, errors, warnings):
    if type(node) is not str:
        error = ValidationError(path, "was expecting a string")
        errors.append(error)
        return

    values = specs['values']
    if node not in values:
        error = ValidationError(path, "enum value is invalid")
        errors.append(error)
        return

    return node

adjust_node_map = {
    'flag'   : process_flag_node,
    'integer': process_integer_node,
    'string' : process_string_node,
    'list'   : process_list_node,
    'tuple'  : process_tuple_node,
    'map'    : process_map_node,
    'decimal': process_decimal_node,
    'enum'   : process_enum_node
}

def adjust_node(path, node, specs, errors, warnings):
    optional = specs.get('option', False)
    if not optional and node is None:
        error = ValueError(path, "value cant be null")
        errors.append(error)
        return
    elif optional and node is None:
        return None
    else:
        return adjust_node_map[specs['type']](path, node, specs, errors, warnings)

def object_to_document(object, specs, errors=None, warnings=None, no_dump=False):
    """ Convert Python object to its JSON equivalent. """

    # Assume specs is valid (Python object form)

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

    document = adjust_node([], object, specs, errors, warnings)
    dumped_document = json.dumps(document)

    # If we're not lazy-validating the specs, we raise the first error that
    # occurred.
    if not lazy_validation and len(errors) > 0:
        raise errors[0]

    if no_dump:
        return document
    else:
        return dumped_document