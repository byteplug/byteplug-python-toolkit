# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document.types import *
import yaml

def test_flag_type():
    flag = Flag(option=True)
    assert flag.to_object() == {'type': 'flag', 'option': True}
    yaml.dump(flag)

def test_integer_type():
    Integer(min=42)
    Integer(min=(42, True))
    Integer(min=(42, False))

    Integer(max=42)
    Integer(max=(42, True))
    Integer(max=(42, False))

    integer = Integer(
        min=10,
        max=(42, True),
        option=True
    )
    assert integer.to_object() == {
        'type': 'integer',
        'minimum': 10,
        'maximum': {
            'exclusive': True,
            'value': 42
        },
        'option': True
    }
    yaml.dump(integer)

def test_string_type():
    String(length=42)
    String(length=(42, None))
    String(length=(None, 42))
    String(length=(0, 42))

    string = String(
        length=(0, 42),
        pattern="^[a-z]+(-[a-z]+)*$",
        option=True
    )
    assert string.to_object() == {
        'type': 'string',
        'length': {
            'minimum': 0,
            'maximum': 42
        },
        'pattern': "^[a-z]+(-[a-z]+)*$",
        'option': True
    }
    yaml.dump(string)

def test_enum_type():
    Enum(['foo', 'bar', 'quz'])

    enum = Enum(
        ['foo', 'bar', 'quz'],
        option=True
    )
    assert enum.to_object() == {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz'],
        'option': True
    }
    yaml.dump(enum)

def test_list_type():
    List(String(), length=42)
    List(String(), length=(42, None))
    List(String(), length=(None, 42))
    List(String(), length=(0, 42))

    list = List(
        String(),
        length=(0, 42),
        option=True
    )
    assert list.to_object() == {
        'type': 'list',
        'value': {'type': 'string'},
        'length': {
            'minimum': 0,
            'maximum': 42
        },
        'option': True
    }
    yaml.dump(list)

def test_tuple_type():
    tuple = Tuple([Flag(), Integer(), String()], option=True)
    assert tuple.to_object() == {
        'type': 'tuple',
        'values': [
            {'type': 'flag'},
            {'type': 'integer'},
            {'type': 'string'}
        ],
        'option': True
    }
    yaml.dump(tuple)

def test_map_type():
    map_ = Map({
        'foo': Flag(),
        'bar': Integer(),
        'quz': String()
    }, option=True)
    assert map_.to_object() == {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'integer'},
            'quz': {'type': 'string'}
        },
        'option': True
    }
    yaml.dump(tuple)
