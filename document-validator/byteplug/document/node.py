# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re

PROPERTIES = {
    'flag'   : [],
    'number' : ['decimal', 'min', 'max'],
    'string' : ['length', 'pattern'],
    'array'  : ['value', 'length'],
    'object' : ['key', 'value', 'length'],
    'tuple'  : ['items'],
    'map'    : ['fields'],
    'enum'   : ['values']
}

class Node:
    def __init__(self, type_, **properties) -> None:
        assert type_ in PROPERTIES.keys(), "type is invalid"

        self.type_ = type_
        self.properties = {}

        self.update_properties(properties)

    def __call__(self, **properties):
        self.update_properties(properties)
        return self

    def to_object(self):
        # TODO; Implement a parameter to remove optional fields when they have
        #       default value (e.g: `option: false`)
        return {'type': self.type_} | self.properties

    def update_properties(self, properties):
        for key, value in properties.items():
            if key == 'name':
                assert type(value) is str, "value of 'name' property must be a string"
                self.properties[key] = value
            elif key == 'description':
                assert type(value) is str, "value of 'description' property must be a string"
                self.properties[key] = value
            elif key in PROPERTIES[self.type_]:
                if key == 'decimal':
                    self.update_decimal_property(value)
                elif key in ['min', 'max']:
                    self.update_min_max_property(key, value)
                elif key == 'length':
                    self.update_length_property(value)
                elif key == 'pattern':
                    self.update_pattern_property(value)
                elif key == 'key':
                    self.update_key_property(value)
                elif key == 'value':
                    self.update_value_property(value)
                elif key == 'items':
                    self.update_tuple_items(value)
                elif key == 'fields':
                    self.update_map_fields(value)
                elif key == 'values':
                    self.update_enum_values(value)
            elif key == 'option':
                assert type(value) is bool, "value of 'option' property must be a boolean"
                self.properties[key] = value
            else:
                raise AssertionError(f"property '{key}' is invalid")

    def update_decimal_property(self, value):
        assert type(value) is bool, "'decimal' value must be a bool"
        self.properties['decimal'] = value

    def update_min_max_property(self, key, value):
        assert key in ['min', 'max']
        property = 'minimum' if key == 'min' else 'maximum'

        if type(value) in [int, float]:
            self.properties[property] = value

        elif type(value) is tuple:
            assert type(value[0]) in [int, float], "first value must be a number"
            assert type(value[1]) is bool, "second value must be a boolean"

            self.properties[property] = {
                'exclusive': value[1],
                'value': value[0]
            }

        else:
            raise AssertionError(f"'{key}' value must be an integer or a tuple")

    def update_length_property(self, value):
        property = 'length'

        if type(value) is int:
            self.properties[property] = value

        elif type(value) in [list, tuple]:
            assert value[0] == None or type(value[0]) is int, "first value must be an integer or None"
            assert value[1] == None or type(value[1]) is int, "second value must be an integer or None"
            assert not (value[0] == None and value[1] == None), "one of the value must be different than None"

            self.properties[property] = {}
            if value[1] is not None:
                self.properties[property]['minimum'] = value[0]
            if value[1] is not None:
                self.properties[property]['maximum'] = value[1]

        else:
            raise AssertionError(f"'length' value must be an integer or a tuple")

    def update_pattern_property(self, value):
        assert type(value) is str, "pattern value must be a string"
        self.properties['pattern'] = value

    def update_key_property(self, value):
        assert value in ['integer', 'string'], "key must be either 'integer' or 'string'"
        self.properties['key'] = value

    def update_value_property(self, value):
        assert type(value) is Node, "value must be another node"
        self.properties['value'] = value.to_object()

    def update_tuple_items(self, items):
        assert type(items) in [list, tuple], "items must be either a list or a tuple"
        for item in items:
            assert type(item) is Node, "items must be nodes"

        self.properties['items'] = list(map(lambda item: item.to_object(), items))

    def update_map_fields(self, fields):
        assert type(fields) is dict, "fields must be a dict"
        for key, value in fields.items():
            assert type(key) is str, "keys must be string"
            assert re.match(r"^[a-zA-Z0-9\-\_]+$", key), "keys must match the regex"
            assert type(value) is Node, "value must be another node"

        self.properties['fields'] = {key: value.to_object() for key, value in fields.items()}

    def update_enum_values(self, values):
        for value in values:
            assert type(value) is str, "values must be string"
            assert re.match(r"^[a-zA-Z0-9\-\_]+$", value), "values must match the regex"

        self.properties['values'] = list(values)
