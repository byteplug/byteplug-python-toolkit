# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

class ValidationError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message

class ValidationWarning(Warning):
    def __init__(self, path, message):
        self.path = path
        self.message = message
