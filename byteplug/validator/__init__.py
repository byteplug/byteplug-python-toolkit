# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.validator.types import *
from byteplug.validator.specs import validate_specs
from byteplug.validator.document import document_to_object
from byteplug.validator.object import object_to_document
from byteplug.validator.exception import ValidationError
