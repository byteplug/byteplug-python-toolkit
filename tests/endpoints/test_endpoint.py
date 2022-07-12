# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.validator.types import *
from byteplug.validator.exception import ValidationError
from byteplug.endpoints.endpoint import endpoint, collection_endpoint, Operate
from byteplug.endpoints.endpoint import request, response, error
import pytest

INVALID_SPECS = {'type': 'foo'}
VALID_SPECS = Map({
    'foo': Flag(),
    'bar': Integer(),
    'quz': String()
}).to_object()

def test_endpoint():
    """ Test the @endpoint decorator. """

    @endpoint("foo", name="Foo", description="Description of 'Foo' endpoint.")
    def foo():
        pass

    assert 'specs' in dir(foo)
    assert foo.specs == {
        'name': "Foo",
        'description': "Description of 'Foo' endpoint.",
        'collection': None,
        'operate': None,
        'path': "foo",
        'authentication': False,
        'request': None,
        'response': None,
        'errors': {},
        'adaptor': None
    }

def test_collection_endpoint():
    """ Test the @collection_endpoint decorator. """

    @collection_endpoint("foo", "bar", name="Foo", description="Description of 'Foo' endpoint.")
    def foo():
        pass

    assert 'specs' in dir(foo)
    assert foo.specs == {
        'name': "Foo",
        'description': "Description of 'Foo' endpoint.",
        'collection': "foo",
        'operate': Operate.COLLECTION,
        'path': "bar",
        'authentication': False,
        'request': None,
        'response': None,
        'errors': {},
        'adaptor': None
    }

    @collection_endpoint("bar", "quz", operate_on_item=True, name="Bar", description="Description of 'Bar' endpoint.")
    def bar():
        pass

    assert 'specs' in dir(bar)
    assert bar.specs == {
        'name': "Bar",
        'description': "Description of 'Bar' endpoint.",
        'collection': "bar",
        'operate': Operate.ITEM,
        'path': "quz",
        'authentication': False,
        'request': None,
        'response': None,
        'errors': {},
        'adaptor': None
    }

def test_request():
    """ Test the @request decorator. """

    # test when not followed by an endpoint decorator
    with pytest.raises(AssertionError, match="decorator must be followed by an endpoint decorator"):
        @request(VALID_SPECS)
        def f(): pass

    # test with an invalid specs
    with pytest.raises(ValidationError, match="value of 'type' is incorrect"):
        @request(INVALID_SPECS)
        @endpoint("foo")
        def f(): pass

    @request(VALID_SPECS)
    @endpoint("foo")
    def f(): pass

    assert f.specs['request'] == VALID_SPECS

def test_response():
    """ Test the @response decorator. """

    # test when not followed by an endpoint decorator
    with pytest.raises(AssertionError, match="decorator must be followed by an endpoint decorator"):
        @response(VALID_SPECS)
        def f(): pass

    # test with an invalid specs
    with pytest.raises(ValidationError, match="value of 'type' is incorrect"):
        @response(INVALID_SPECS)
        @endpoint("foo")
        def f(): pass

    @response(VALID_SPECS)
    @endpoint("foo")
    def f(): pass

    assert f.specs['response'] == VALID_SPECS

def test_error():
    """ Test the @error decorator. """

    # test when not followed by an endpoint decorator
    with pytest.raises(AssertionError, match="decorator must be followed by an endpoint decorator"):
        @error("foo", VALID_SPECS)
        def f(): pass

    # test with an invalid tag name
    with pytest.raises(AssertionError, match="invalid tag name"):
        @error("-foo", VALID_SPECS)
        @endpoint("bar")
        def f(): pass

    # test with an invalid specs
    with pytest.raises(ValidationError, match="value of 'type' is incorrect"):
        @error("foo", INVALID_SPECS)
        @endpoint("bar")
        def f(): pass

    # test two errors with same tag name
    with pytest.raises(AssertionError, match="errors with same tag name is not allowed"):
        @error("foo", VALID_SPECS)
        @error("foo", VALID_SPECS)
        @endpoint("bar")
        def f(): pass

    another_valid_specs = String().to_object()

    @error("foo", VALID_SPECS, name="Foo", description="Description of 'Foo' error.")
    @error("bar", another_valid_specs)
    @endpoint("quz")
    def f(): pass

    assert f.specs['errors'] == {
        'foo': {
            'name': "Foo",
            'description': "Description of 'Foo' error.",
            'specs': VALID_SPECS
        },
        'bar': {
            'name': None,
            'description': None,
            'specs': another_valid_specs
        }
    }

def test_adaptor():
    """ Test the @adaptor decorator. """

    # TODO; To be implemented.
    pass
