# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

from byteplug.validator.types import *
from byteplug.endpoints.endpoint import request, response, error
from byteplug.endpoints.endpoint import endpoint, collection_endpoint
from byteplug.endpoints.endpoints import Endpoints

def test_specs():
    # Test the three kinds of endpoints and the four possible request/response
    # scenarios, then see how it's generating the YAML specs. Also adds some
    # records to the mix.

    foobar_specs = String(pattern="foobar")
    barfoo_specs = String(pattern="barfoo")

    @request(Integer().to_object())
    @error("error-a", Flag().to_object())
    @error("error-b", Integer().to_object())
    @error("error-c", String().to_object())
    @endpoint("foo", name="Foo", description="Description of 'Foo' endpoint.")
    def foo():
        pass

    @response(Integer().to_object())
    @collection_endpoint("bar", "action1", authentication=True)
    def bar():
        pass

    @request(Integer().to_object())
    @response(String().to_object())
    @error("error-z", String().to_object(), name="Error Z", description="Description of 'Error Z' error.")
    @collection_endpoint("quz", "action2", operate_on_item=True)
    def quz():
        pass

    @endpoint("yolo")
    def yolo():
        pass

    contact = {
        "name": "My Company",
        "url": "https://www.my-company.com/",
        "email": "contact@my-company.com"
    }

    license = {
        "name": "The Open Software License 3.0",
        "url": "https://opensource.org/licenses/OSL-3.0"
    }

    version = "1.0.0"

    endpoints = Endpoints('test', "Test", "Description of 'Test' endpoints.", contact, license, version)
    endpoints.add_record("foobar", foobar_specs)
    endpoints.add_record("barfoo", barfoo_specs)

    endpoints.add_collection("bar", name="Bar", description="Description of 'Bar' collection.")
    endpoints.add_collection("quz")

    endpoints.add_endpoint(foo)
    endpoints.add_endpoint(bar)
    endpoints.add_endpoint(quz)
    endpoints.add_endpoint(yolo)

    block = endpoints.generate_specs(to_string=False)

    assert block == {
        'standard': "https://www.byteplug.io/standards/easy-endpoints/1.0",
        'title': "Test",
        'summary': "Description of 'Test' endpoints.",
        'contact': {
            'name' : "My Company",
            'url'  : "https://www.my-company.com/",
            'email': "contact@my-company.com"
        },
        'license': {
            'name': "The Open Software License 3.0",
            'url' : "https://opensource.org/licenses/OSL-3.0"
        },
        'version': '1.0.0',
        'records': {
            'foobar': {
                'type': 'string',
                'pattern': 'foobar'
            },
            'barfoo': {
                'type': 'string',
                'pattern': 'barfoo'
            }
        },
        'endpoints': {
            'foo': {
                'name': "Foo",
                'description': "Description of 'Foo' endpoint.",
                'request': {
                    'type': 'integer'
                },
                'errors': {
                    'error-a': {
                        'value': {
                            'type': 'flag'
                        }
                    },
                    'error-b': {
                        'value': {
                            'type': 'integer'
                        }
                    },
                    'error-c': {
                        'value': {
                            'type': 'string'
                        }
                    }
                }
            },
            'yolo': {} # TODO; Review this.
        },
        'collections': {
            'bar': {
                'name': "Bar",
                'description': "Description of 'Bar' collection.",
                'endpoints': {
                    'action1': {
                        'operate': 'collection',
                        'authentication': True,
                        'response': {
                            'type': 'integer'
                        }
                    }
                }
            },
            'quz': {
                'endpoints': {
                    'action2': {
                        'operate': 'item',
                        'request': {
                            'type': 'integer'
                        },
                        'response': {
                            'type': 'string'
                        },
                        'errors': {
                            'error-z': {
                                'name': "Error Z",
                                'description': "Description of 'Error Z' error.",
                                'value': {
                                    'type': 'string'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
