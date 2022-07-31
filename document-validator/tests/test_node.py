# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document.node import Node
import yaml

def test_type():
    for type_ in ['flag', 'number', 'string']:
        node = Node(type_)

        assert node.to_object() == {'type': type_}

        assert node(option=True).to_object() == {
            'type': type_,
            'option': True
        }

        description = "This is the description of 'My Node' node."
        assert node(name="My Node", description=description).to_object() == {
            'type': type_,
            'name': "My Node",
            'description': description,
            'option': True
        }

def test_flag_type():
    flag = Node('flag', option=True)
    assert flag.to_object() == {'type': 'flag', 'option': True}
    yaml.dump(flag)

def test_number_type():
    Node('number', min=42)
    Node('number', min=(42, True))
    Node('number', min=(42, False))

    Node('number', max=42)
    Node('number', max=(42, True))
    Node('number', max=(42, False))

    number = Node('number',
        min=10,
        max=(42, True),
        option=True
    )
    assert number.to_object() == {
        'type': 'number',
        'minimum': 10,
        'maximum': {
            'exclusive': True,
            'value': 42
        },
        'option': True
    }
    yaml.dump(number)

def test_string_type():
    Node('string', length=42)
    Node('string', length=(42, None))
    Node('string', length=(None, 42))
    Node('string', length=(0, 42))

    string = Node('string',
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

def test_array_type():
    Node('array', value=Node('string'), length=42)
    Node('array', value=Node('string'), length=(42, None))
    Node('array', value=Node('string'), length=(None, 42))
    Node('array', value=Node('string'), length=(0, 42))

    node = Node('array',
        value=Node('string'),
        length=(0, 42),
        option=True
    )
    assert node.to_object() == {
        'type': 'array',
        'value': {'type': 'string'},
        'length': {
            'minimum': 0,
            'maximum': 42
        },
        'option': True
    }
    yaml.dump(node)

def test_object_type():
    Node('object', value=Node('string'), key='integer', length=42)
    Node('object', value=Node('string'), key='integer', length=(42, None))
    Node('object', value=Node('string'), key='string', length=(None, 42))
    Node('object', value=Node('string'), key='string', length=(0, 42))

    node = Node('object',
        key='integer',
        value=Node('string'),
        length=(0, 42),
        option=True
    )
    assert node.to_object() == {
        'type': 'object',
        'key': 'integer',
        'value': {'type': 'string'},
        'length': {
            'minimum': 0,
            'maximum': 42
        },
        'option': True
    }
    yaml.dump(node)

def test_tuple_type():
    tuple = Node('tuple', items=[
        Node('flag'),
        Node('number'),
        Node('string')
    ], option=True)

    assert tuple.to_object() == {
        'type': 'tuple',
        'items': [
            {'type': 'flag'},
            {'type': 'number'},
            {'type': 'string'}
        ],
        'option': True
    }
    yaml.dump(tuple)

def test_map_type():
    node = Node('map', fields={
        'foo': Node('flag'),
        'bar': Node('number'),
        'quz': Node('string')
    }, option=True)

    assert node.to_object() == {
        'type': 'map',
        'fields': {
            'foo': {'type': 'flag'},
            'bar': {'type': 'number'},
            'quz': {'type': 'string'}
        },
        'option': True
    }
    yaml.dump(node)

def test_enum_type():
    Node('enum', values=['foo', 'bar', 'quz'])

    enum = Node('enum',
        values=['foo', 'bar', 'quz'],
        option=True
    )
    assert enum.to_object() == {
        'type': 'enum',
        'values': ['foo', 'bar', 'quz'],
        'option': True
    }
    yaml.dump(enum)
