# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

def read_minimum_value(specs):
    assert specs['type'] in ('integer', 'decimal')

    minimum = specs.get('minimum')
    if minimum is not None:
        if type(minimum) in (int, float):
            return (False, minimum)
        else:
            exclusive = minimum.get('exclusive', False)
            value = minimum['value']
            return (exclusive, value)

def read_maximum_value(specs):
    assert specs['type'] in ('integer', 'decimal')

    maximum = specs.get('maximum')
    if maximum is not None:
        if type(maximum) in (int, float):
            return (False, maximum)
        else:
            exclusive = maximum.get('exclusive', False)
            value = maximum['value']
            return (exclusive, value)
