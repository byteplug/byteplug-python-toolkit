# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

# TODO; Figure out why the 'response' decorator would not work when the
#       endpoint is nested inside the test function, and without this local
#       import statement.
#
# `UnboundLocalError: local variable 'response' referenced before assignment`
#
# This is why you find those imports in each individual tests.
#

import time
from multiprocessing import Process
import requests
from byteplug.document.types import *
from byteplug.endpoints.endpoint import request, error
from byteplug.endpoints.endpoint import adaptor
from byteplug.endpoints.endpoint import endpoint, collection_endpoint
from byteplug.endpoints.endpoints import Endpoints
from byteplug.endpoints.exception import EndpointError
import pytest

def build_url(route, port=8080):
    return "http://127.0.0.1:{0}{1}".format(port, route)

def start_server(endpoints, port):
    endpoints.flask.config.update({
        "THREADED": False,
        "DEBUG": False,
        "TESTING": True,
    })

    # Create a separate process that runs the web server.
    def run_server(endpoints):
        # TODO; make sure it's running no thread/no debug

        endpoints.run('127.0.0.1', port)

    process = Process(target=run_server, args=(endpoints,))

    # Start the server and give it some time to initialize.
    process.start()
    time.sleep(0.1)

    return process

def stop_server(process, port):
    # Send a CTRL+C signal (SIGTERM) to the server process and wait until it
    # returns.
    process.terminate()
    process.join()

def test_endpoints():
    """ Test non-collection endpoint (basic tests). """

    from byteplug.endpoints.endpoint import response

    @request(String(pattern="foo").to_object())
    @response(String(pattern="bar").to_object())
    @endpoint("foobar")
    def foobar(document):
        assert document == "foo"
        return "bar"

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foobar)

    server = start_server(endpoints, 8081)

    url = build_url('/foobar', 8081)
    response = requests.post(url, json='"foo"')
    assert response.status_code == 200
    assert response.json() == "bar"

    stop_server(server, 8081)

def test_collections():
    """ Test collection endpoints (basic tests). """

    from byteplug.endpoints.endpoint import response

    @response(String(pattern="foo/bar").to_object())
    @collection_endpoint("foo", "bar")
    def bar():
        return "foo/bar"

    @response(String(pattern="foo/quz").to_object())
    @collection_endpoint("foo", "quz", operate_on_item=True)
    def quz(item):
        assert item == "42"
        return "foo/quz"

    endpoints = Endpoints("test")
    endpoints.add_collection("foo")
    endpoints.add_endpoint(bar)
    endpoints.add_endpoint(quz)

    server = start_server(endpoints, 8082)

    # test calling a collection endpoint operating on the collection
    url = build_url('/foo/bar', 8082)
    response = requests.post(url)
    assert response.status_code == 200
    assert response.json() == "foo/bar"

    # test calling a collection endpoint operating on an item
    url = build_url('/foo/42/quz', 8082)
    response = requests.post(url)
    assert response.status_code == 200
    assert response.json() == "foo/quz"

    stop_server(server, 8082)

def test_request():
    """ Test request-related functionalities.

    Test triggering the four possible client-side errors.

    - 'json-body-expected'
    - 'body-not-json-format'
    - 'json-body-specs-mismatch'
    - 'no-json-body-expected'

    And also test calling the endpoints with @request correctly.
    """

    @endpoint("foo")
    def foo():
        pass

    @request(String().to_object())
    @endpoint("bar")
    def bar(_document):
        pass

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foo)
    endpoints.add_endpoint(bar)

    server = start_server(endpoints, 8083)

    # test triggering the 'no-json-body-expected' client-side error
    url = build_url('/foo', 8083)
    response = requests.post(url, json={'foo': 'bar'})
    assert response.status_code == 400
    assert response.json() == {
        'kind': 'client-side-error',
        'code': 'no-json-body-expected',
        'name': "No JSON body was expected",
        'description': "This endpoint did not expect a body in the HTTP request."
    }

    # test calling the 'foo' endpoint correctly
    url = build_url('/foo', 8083)
    response = requests.post(url)
    assert response.status_code == 204
    assert response.text == ''

    # test triggering the 'json-body-expected' client-side error
    url = build_url('/bar', 8083)
    response = requests.post(url)
    assert response.status_code == 400
    assert response.json() == {
        'kind': 'client-side-error',
        'code': 'json-body-expected',
        'name': "A JSON body was expected",
        'description': "This endpoint expected a JSON body in the HTTP request."
    }

    # test triggering the 'body-not-json-format' client-side error
    url = build_url('/bar', 8083)
    response = requests.post(url, data="Hello world!")
    assert response.status_code == 400
    assert response.json() == {
        'kind': 'client-side-error',
        'code': 'body-not-json-format',
        'name': "The body is not JSON format",
        'description': "The format of the body in the HTTP request must be JSON."
    }

    # test triggering the 'json-body-specs-mismatch' client-side error
    url = build_url('/bar', 8083)
    response = requests.post(url, json="42")
    assert response.status_code == 400
    assert response.json() == {
        'kind': 'client-side-error',
        'code': 'json-body-specs-mismatch',
        'name': "The JSON body does not match the specs",
        'description': "The JSON body in the HTTP request does not match the specifications.",
        'errors': [{'path': 'root', 'message': "was expecting a JSON string"}],
        'warnings': []
    }

    # test calling the 'bar' endpoint correctly
    url = build_url('/bar', 8083)
    response = requests.post(url, json='"Hello world!"')
    assert response.status_code == 204
    assert response.text == ''

    stop_server(server, 8083)

def test_response():
    """ Test response-related functionalities.

    Test triggering the 'invalid-response-specs-mismatch' server-side error and
    test calling the endpoints with @response in various scenarios.
    """

    from byteplug.endpoints.endpoint import response

    @endpoint("foo-with-response")
    def foo_with_response():
        return "Hello world!"

    @endpoint("foo-with-no-response")
    def foo_with_no_response():
        pass

    @response(String().to_object())
    @endpoint("bar-with-response")
    def bar_with_response():
        return "Hello world!"

    @response(String().to_object())
    @endpoint("bar-with-invalid-response")
    def bar_with_invalid_response():
        return 42

    @response(String().to_object())
    @endpoint("bar-with-no-response")
    def bar_with_no_response():
        pass

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foo_with_response)
    endpoints.add_endpoint(foo_with_no_response)
    endpoints.add_endpoint(bar_with_response)
    endpoints.add_endpoint(bar_with_invalid_response)
    endpoints.add_endpoint(bar_with_no_response)

    server = start_server(endpoints, 8094)

    # Port 8084 seems unavailable on some Github runners.
    url = build_url('/foo-with-response', 8094)
    response = requests.post(url)
    assert response.status_code == 204
    assert response.text == ''

    url = build_url('/foo-with-no-response', 8094)
    response = requests.post(url)
    assert response.status_code == 204
    assert response.text == ''

    url = build_url('/bar-with-response', 8094)
    response = requests.post(url)
    assert response.status_code == 200
    assert response.json() == "Hello world!"

    # test triggering the 'invalid-response-specs-mismatch' server-side error
    url = build_url('/bar-with-invalid-response', 8094)
    response = requests.post(url)
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'server-side-error',
        'code': 'invalid-response-specs-mismatch',
        'name': "Invalid returned response JSON body",
        'description': "The endpoint did not return a response JSON body matching its specifications.",
        'errors': [{'path': 'root', 'message': "was expecting a string"}],
        'warnings': []
    }

    # TODO; FIX THIS
    # url = build_url('/bar-with-no-response', 8094)
    # response = requests.post(url)
    # assert response.status_code == 500
    # assert response.json() == {
    #     'kind': 'server-side-error',
    #     'code': 'invalid-response-specs-mismatch',
    #     'name': "Invalid returned response JSON body",
    #     'description': "The endpoint did not return a response JSON body matching its specifications.",
    #     'errors': [{'path': 'root', 'message': "was expecting a string"}],
    #     'warnings': []
    # }

    stop_server(server, 8094)

def test_errors():
    """ Test error-related functionalities.

    Test triggering the following three server-side errors.

    - 'invalid-error'
    - 'invalid-error-specs-mismatch'
    - 'unhandled-error'

    And also test calling the endpoints with @error correctly.
    """

    from byteplug.endpoints.endpoint import response

    @request(Enum(values=[
        'foo', 'bar', 'quz', 'yolo',
        'specs-mismatch',
        'invalid-error',
        'unhandled-error'
    ]).to_object())
    @error("foo", Flag().to_object(),    "Foo", "Description of 'Foo' error.")
    @error("bar", Integer().to_object(), name="Bar")
    @error("quz", String().to_object(),  description="Description of 'Quz' error.")
    @error("yolo") # This is an error with no specs
    @endpoint("foobar")
    def foobar(document):
        if document == 'foo':
            raise EndpointError('foo', False)
        elif document == 'bar':
            raise EndpointError('bar', 42)
        elif document == 'quz':
            raise EndpointError('quz', "Hello world!")
        elif document == 'yolo':
            raise EndpointError('yolo', None)
        elif document == 'specs-mismatch':
            raise EndpointError('quz', 42)
        elif document == 'invalid-error':
            raise EndpointError('oloy')
        elif document == 'unhandled-error':
            raise RuntimeError

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foobar)

    server = start_server(endpoints, 8085)

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"foo"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'error',
        'code': 'foo',
        'name': "Foo",
        'description': "Description of 'Foo' error.",
        'value': False
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"bar"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'error',
        'code': 'bar',
        'name': "Bar",
        'value': 42
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"quz"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'error',
        'code': 'quz',
        'description': "Description of 'Quz' error.",
        'value': "Hello world!"
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"yolo"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'error',
        'code': 'yolo'
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"specs-mismatch"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'server-side-error',
        'code': 'invalid-error-specs-mismatch',
        'name': "Invalid returned error JSON body",
        'description': "The endpoint did not return an error JSON body matching its specifications.",
        'errors': [{'path': 'root', 'message': 'was expecting a string'}],
        'warnings': []
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"invalid-error"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'server-side-error',
        'code': 'invalid-error',
        'name': "Invalid returned error",
        'description': "The endpoint returned an unexpected error (not listed in its specifications)."
    }

    url = build_url('/foobar', 8085)
    response = requests.post(url, json='"unhandled-error"')
    assert response.status_code == 500
    assert response.json() == {
        'kind': 'server-side-error',
        'code': 'unhandled-error',
        'name': "Unhandled error",
        'description': "An unexpected and unhandled error occurred during the execution of the endpoint."
    }


    stop_server(server, 8085)

def test_authentication():
    """ Test functionalities to authentication.

    To be written.
    """

    from byteplug.endpoints.endpoint import response

    @endpoint("foo", authentication=True)
    def foo(token):
        assert token == "abcd1234"

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foo)

    server = start_server(endpoints, 8086)

    # test without a token
    url = build_url('/foo', 8086)
    response = requests.post(url)
    assert response.status_code == 401
    # assert response.text == ""

    # test with a token
    token = "abcd1234"
    headers = {"Authorization": f"Bearer {token}"}
    url = build_url('/foo', 8086)
    response = requests.post(url, headers=headers)
    assert response.status_code == 204

    # TODO; More tests should be performed.
    #
    # - test request with an invalid token ?
    # - test request with an authentication header of the wrong format
    # - test sensitivity ?
    # - what if endpoint is not protected and a token is passed
    #

    stop_server(server, 8086)

def test_adaptor_decorator():
    """ To be written.

    To be written.
    """

    # The @adaptor decorator is a feature that was designed for Bytpelug own
    # need without many thoughts about more general applications. Therefore,
    # this unit test is only testing its canonical application.
    from byteplug.endpoints.endpoint import response

    def my_adaptor(token=None, item=None, document=None):
        args = []
        # unpack token
        if token:
            args.append("abcd1234")

        if item:
            args.append('42')

        if document:
            if type(document) is dict:
                args.extend(list(document.values()))
            else:
                args.append(document)

        return args

    request_specs = Map({
        'foo': Flag(),
        'bar': Integer(),
        'quz': String()
    }).to_object()

    document_value = '{"foo": false, "bar": 42, "quz": "Hello world!"}'

    @request(request_specs)
    @response(String().to_object())
    @adaptor(my_adaptor)
    @endpoint("foo")
    def foo(foo, bar, quz):
        assert foo == False
        assert bar == 42
        assert quz == "Hello world!"

        return "foo"

    @request(request_specs)
    @response(String().to_object())
    @adaptor(my_adaptor)
    @collection_endpoint("quz", "foo", operate_on_item=True)
    def quz_foo(item, foo, bar, quz):
        assert item == "42"
        assert foo == False
        assert bar == 42
        assert quz == "Hello world!"

        return "quz/foo"

    @request(request_specs)
    @response(String().to_object())
    @adaptor(my_adaptor)
    @collection_endpoint("quz", "bar", operate_on_item=True, authentication=True)
    def quz_bar(user_id, item, foo, bar, quz):
        user_id == "abcd1234"
        assert item == "42"
        assert foo == False
        assert bar == 42
        assert quz == "Hello world!"

        return "quz/bar"

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foo)
    endpoints.add_collection("quz")
    endpoints.add_endpoint(quz_foo)
    endpoints.add_endpoint(quz_bar)

    server = start_server(endpoints, 8087)

    url = build_url('/foo', 8087)
    response = requests.post(url, json=document_value)
    assert response.status_code == 200
    assert response.json() == "foo"

    url = build_url('/quz/42/foo', 8087)
    response = requests.post(url, json=document_value)
    assert response.status_code == 200
    assert response.json() == "quz/foo"

    url = build_url('/quz/42/bar', 8087)
    headers = {"Authorization": "Bearer abcd1234"}
    response = requests.post(url, json=document_value, headers=headers)
    assert response.status_code == 200
    assert response.json() == "quz/bar"

    stop_server(server, 8087)

# TODO; Implemented the following unit test.
def test_specs_endpoint():
    """ To be written.

    To be written.
    """

    # TODO; This test should be more developed and more accurate (more
    #       endpoints, and carefully check every part of the JSON/YAML
    #       response).
    #

    @endpoint("foo")
    def foo():
        pass

    endpoints = Endpoints("test")
    endpoints.add_endpoint(foo)
    endpoints.add_expose_specs_endpoint('/my-yaml-specs')
    endpoints.add_expose_specs_endpoint('/my-json-specs', no_yaml=True)

    server = start_server(endpoints, 8088)

    url = build_url('/my-yaml-specs', 8088)
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text.startswith("standard: https://www.byteplug.io/standards/easy-endpoints/1.0")

    url = build_url('/my-json-specs', 8088)
    response = requests.get(url)
    assert response.status_code == 200
    json_response = response.json()
    assert 'standard' in json_response
    assert json_response['standard'] == "https://www.byteplug.io/standards/easy-endpoints/1.0"

    stop_server(server, 8088)
