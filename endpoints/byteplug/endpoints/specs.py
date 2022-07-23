# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document.exception import ValidationError, ValidationWarning

__all__ = ['validate_specs']

def validate_specs(specs, errors=None, warnings=None):
    """ Validate the YAML specs.

    To be written.
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

    # TODO; To be implemented.

    # If we're not lazy-validating the specs, we raise the first error that
    # occurred.
    if not lazy_validation and len(errors) > 0:
        raise errors[0]
