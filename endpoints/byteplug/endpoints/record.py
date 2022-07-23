# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.document.types import Type

class Record(Type):
    records_map = {}

    def __init__(self, name):
        Type.__init__(self, option=False)
        self.name = name

    def to_object(self):
        return self.name
