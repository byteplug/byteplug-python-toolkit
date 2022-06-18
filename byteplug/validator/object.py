# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
import json
from byteplug.validator.utils import read_minimum_value, read_maximum_value
from byteplug.validator.exception import ValidationError

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

def process_flag_node(path, node, specs):
    if type(node) is not bool:
        raise ValidationError(path, "was expecting a boolean")

    return node

def process_integer_node(path, node, specs):
    if type(node) is not int:
        raise ValidationError(path, "was expecting an integer")

    minimum = read_minimum_value(specs)
    maximum = read_maximum_value(specs)

    if minimum:
        is_exclusive, value = minimum
        if is_exclusive:
            if not (node > value):
                raise ValidationError(path, "value must be strictly greater than X")
        else:
            if not (node >= value):
                raise ValidationError(path, "value must be equal or greater than X")

    if maximum:
        is_exclusive, value = maximum
        if is_exclusive:
            if not (node < value):
                raise ValidationError(path, "value must be strictly less than X")
        else:
            if not (node <= value):
                raise ValidationError(path, "value must be equal or less than X")

    return node

def process_decimal_node(path, node, specs):
    pass

def process_string_node(path, node, specs):
    if type(node) is not str:
        raise ValidationError(path, "was expecting a string")

    length = specs.get('length')
    if length is not None:
        if type(length) is int:
            if len(node) != length:
                raise ValidationError(path, "length of string must be equal to X")
        else:
            minimum = length.get("minimum")
            maximum = length.get("maximum")

            if minimum:
                if not (len(node) >= minimum):
                    raise ValidationError(path, "length of string must be greater or equal to X")

            if maximum:
                if not (len(node) <= maximum):
                    raise ValidationError(path, "length of string must be lower or equal to X")

    pattern = specs.get('pattern')
    if pattern is not None:
        if not re.match(pattern, node):
            raise ValidationError(path, "didnt match pattern")

    return node

def process_enum_node(path, node, specs):
    if type(node) is not str:
        raise ValidationError(path, "was expecting a string")

    values = specs['values']
    if node not in values:
        raise ValidationError(path, "value was expected to be one of [foo, bar, quz]")

    return node

def process_list_node(path, node, specs):
    value = specs['value']

    if type(node) is not list:
        raise ValidationError(path, "was expecting a list")

    length = specs.get('length')
    if length is not None:
        if type(length) is int:
            if len(node) != length:
                raise ValidationError(path, "length of list must be equal to X")
        else:
            minimum = length.get("minimum")
            maximum = length.get("maximum")

            if minimum:
                if not (len(node) >= minimum):
                    raise ValidationError(path, "length of list must be greater or equal to X")

            if maximum:
                if not (len(node) <= maximum):
                    raise ValidationError(path, "length of list must be lower or equal to X")


    # TODO; Rework this.
    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_node.append(adjust_node(path + '.[' + str(index) + ']', item, value))

    return adjusted_node

def process_tuple_node(path, node, specs):
    values = specs['values']

    if type(node) is not tuple:
        raise ValidationError(path, "was expecting a tuple")

    if len(node) != len(values):
        raise ValidationError(path, "was expecting tuple of N elements")

    # TODO; Rework this.
    adjusted_node = []
    for (index, item) in enumerate(node):
        adjusted_node.append(
            adjust_node(path + '.(' + str(index) + ')', item, values[index])
        )

    return adjusted_node

def process_map_node(path, node, specs):
    fields = specs['fields']

    if type(node) is not dict:
        raise ValidationError(path, "was expecting a dict")

    # TODO; More things to do here.
    adjusted_node = {}
    for key, value in fields.items():
        if key in node:
            adjusted_node[key] = adjust_node(path + f'.{key}', node[key], value)

    return adjusted_node

adjust_node_map = {
    'flag'   : process_flag_node,
    'integer': process_integer_node,
    'decimal': process_decimal_node,
    'string' : process_string_node,
    'enum'   : process_enum_node,
    'list'   : process_list_node,
    'tuple'  : process_tuple_node,
    'map'    : process_map_node
}

def adjust_node(path, node, specs):
    optional = specs.get('option', False)
    if not optional and node is None:
        raise ValueError(path, "value cant be null")
    elif optional and node is None:
        return None
    else:
        return adjust_node_map[specs['type']](path, node, specs)

def object_to_document(object, specs):
    """ Convert Python object to its JSON equivalent. """

    document = adjust_node("root", object, specs)
    return json.dumps(document)
