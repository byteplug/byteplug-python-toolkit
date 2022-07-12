# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

import re
from enum import Enum
from byteplug.validator.specs import validate_specs

Operate = Enum('Operate', 'ITEM COLLECTION')

def request(specs):
    validate_specs(specs)
    def decorator(function):
        assert "specs" in dir(function), "the @request decorator must be followed by an endpoint decorator"
        function.specs['request'] = specs
        return function

    return decorator

def response(specs):
    validate_specs(specs)
    def decorator(function):
        assert "specs" in dir(function), "the @response decorator must be followed by an endpoint decorator"
        function.specs['response'] = specs
        return function

    return decorator

def error(tag, specs, name=None, description=None):
    assert re.match(r"^[a-z]+(-[a-z]+)*$", tag), "invalid tag name"
    validate_specs(specs)

    def decorator(function):
        assert "specs" in dir(function), "the @error decorator must be followed by an endpoint decorator"

        assert tag not in function.specs['errors'], "errors with same tag name is not allowed"
        function.specs['errors'][tag] = {
            'name': name,
            'description': description,
            'specs': specs
        }

        return function

    return decorator

def adaptor(f):
    # TODO; check adaptor signature (catch early mistakes)
    pass

    def decorator(function):
        assert "specs" in dir(function), "the @adaptor decorator must be followed by an endpoint decorator"

        function.specs['adaptor'] = f

        return function

    return decorator

def make_endpoint_decorator(collection, operate, path, authentication, name, description):
    def decorator(function):
        function.specs = {
            'name': name,
            'description': description,
            'collection': collection,
            'operate': operate,
            'path': path,
            'authentication': authentication,
            'request': None,
            'response': None,
            'errors': {},
            'adaptor': None
        }

        return function
    return decorator

def endpoint(path, authentication=False, name=None, description=None):
    return make_endpoint_decorator(None, None, path, authentication, name, description)

def collection_endpoint(collection, path, operate_on_item=False, authentication=False, name=None, description=None):
    operate = Operate.ITEM if operate_on_item else Operate.COLLECTION
    return make_endpoint_decorator(collection, operate, path, authentication, name, description)
