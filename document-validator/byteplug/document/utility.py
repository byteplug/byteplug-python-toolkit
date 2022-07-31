# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document.exception import ValidationError

def read_minimum_value(specs):
    assert specs['type'] == 'number'

    minimum = specs.get('minimum')
    if minimum is not None:
        if type(minimum) in (int, float):
            return (False, minimum)
        else:
            exclusive = minimum.get('exclusive', False)
            value = minimum['value']
            return (exclusive, value)

def read_maximum_value(specs):
    assert specs['type'] == 'number'

    maximum = specs.get('maximum')
    if maximum is not None:
        if type(maximum) in (int, float):
            return (False, maximum)
        else:
            exclusive = maximum.get('exclusive', False)
            value = maximum['value']
            return (exclusive, value)

def check_length(value, length, path, errors, warnings):
    if length is not None:
        if type(length) in (int, float):
            length = int(length)

            if value != length:
                error = ValidationError(path, f"length must be equal to {length}")
                errors.append(error)
                return
        else:
            minimum = length.get("minimum")
            maximum = length.get("maximum")

            if minimum is not None:
                minimum = int(minimum)

                if not (value >= minimum):
                    error = ValidationError(path, f"length must be equal or greater than {minimum}")
                    errors.append(error)
                    return

            if maximum is not None:
                maximum = int(maximum)

                if not (value <= maximum):
                    error = ValidationError(path, f"length must be equal or lower than {maximum}")
                    errors.append(error)
                    return
