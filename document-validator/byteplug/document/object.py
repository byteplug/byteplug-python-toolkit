# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
import json
from byteplug.document.node import Node
from byteplug.document.utility import read_minimum_value, read_maximum_value
from byteplug.document.utility import check_length
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

def process_number_node(path, node, specs, errors, warnings):
    decimal = specs.get('decimal', True)
    minimum = read_minimum_value(specs)
    maximum = read_maximum_value(specs)

    if type(node) not in (int, float):
        error = ValidationError(path, "was expecting an integer or float")
        errors.append(error)
        return

    if decimal == False and type(node) is float:
        error = ValidationError(path, "was expecting non-decimal number")
        errors.append(error)
        return

    node_errors = []

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

def process_string_node(path, node, specs, errors, warnings):
    if type(node) is not str:
        error = ValidationError(path, "was expecting a string")
        errors.append(error)
        return

    node_errors = []

    length = specs.get('length')
    check_length(len(node), length, path, errors, warnings)

    pattern = specs.get('pattern')
    if pattern is not None:
        if not re.match(pattern, node):
            error = ValidationError(path, "value did not match the pattern")
            node_errors.append(error)

    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return node

def process_array_node(path, node, specs, errors, warnings):
    value = specs['value']

    if type(node) is not list:
        error = ValidationError(path, "was expecting a list")
        errors.append(error)
        return

    length = specs.get('length')
    check_length(len(node), length, path, errors, warnings)

    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_item = adjust_node(path + ['[' + str(index) + ']'], item, value, errors, warnings)
        adjusted_node.append(adjusted_item)

    return adjusted_node

def process_object_node(path, node, specs, errors, warnings):
    key = specs['key']
    value = specs['value']

    if type(node) is not dict:
        error = ValidationError(path, "was expecting a dict")
        errors.append(error)
        return

    length = specs.get('length')
    check_length(len(node), length, path, errors, warnings)

    adjusted_node = {}
    for (index, item) in enumerate(node.items()):
        if key == 'integer':
            if type(item[0]) is not int:
                error = ValidationError(path, f"key at index {index} is invalid; expected it to be an integer")
                errors.append(error)
                continue

            node_key = str(item[0])

        elif key == 'string':
            # Keys are restricted by a given pattern; check value against it.
            # If it doesn't pass the test, the JSON document is invalid.
            if not re.match(r"^[a-zA-Z0-9\-\_]+$", item[0]):
                error = ValidationError(path, f"key at index {index} is invalid; expected to match the pattern")
                errors.append(error)
                continue

            node_key = item[0]

        adjusted_value = adjust_node(path + ['{' + str(item[0]) + '}'], item[1], value, errors, warnings)
        adjusted_node[node_key] = adjusted_value

    return adjusted_node

def process_tuple_node(path, node, specs, errors, warnings):
    items = specs['items']

    if type(node) is not tuple:
        error = ValidationError(path, "was expecting a tuple")
        errors.append(error)
        return

    if len(node) != len(items):
        error = ValidationError(path, f"length of the tuple must be {len(items)}")
        errors.append(error)
        return

    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_item = adjust_node(path + ['<' + str(index) + '>'], item, items[index], errors, warnings)
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
            adjusted_node[key] = adjust_node(path + ['$' + key], value, fields[key], errors, warnings)
        else:
            error = ValidationError(path, f"'{key}' field was unexpected")
            errors.append(error)

    missing_keys = set(fields.keys()) - set(adjusted_node.keys())
    for key in missing_keys:
        if not fields[key].get('option', False):
            error = ValidationError(path, f"'{key}' field was missing")
            errors.append(error)
        else:
            # We insert a 'null' value when the key is missing and the item is
            # optional.
            adjusted_node[key] = None


    if len(node_errors) > 0:
        errors.extend(node_errors)
        return

    return adjusted_node

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
    'number' : process_number_node,
    'string' : process_string_node,
    'array'  : process_array_node,
    'object' : process_object_node,
    'tuple'  : process_tuple_node,
    'map'    : process_map_node,
    'enum'   : process_enum_node
}

def adjust_node(path, node, specs, errors, warnings):
    # We accept a None value if the type is marked as optional.
    optional = specs.get('option', False)
    if optional and node is None:
        return None

    return adjust_node_map[specs['type']](path, node, specs, errors, warnings)

def object_to_document(object, specs, errors=None, warnings=None, no_dump=False):
    """ Convert Python object to its JSON equivalent. """

    if type(specs) is Node:
        specs = specs.to_object()

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