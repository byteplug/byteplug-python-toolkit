# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, July 2022

import re
import yaml
from flask import Flask, request
from flask_cors import CORS
from byteplug.document.object import object_to_document
from byteplug.document.specs import validate_specs
from byteplug.document.document import document_to_object
from byteplug.document.exception import ValidationError, ValidationWarning
from byteplug.endpoints.record import Record
from byteplug.endpoints.endpoint import Operate
from byteplug.endpoints.exception import EndpointError
from byteplug.endpoints.utils import invalid_response_specs_mismatch, json_body_expected, body_not_json_format, json_body_specs_mismatch, no_json_body_expected
from byteplug.endpoints.utils import invalid_error_specs_mismatch, invalid_error, invalid_error_specs_mismatch, unhandled_error
from byteplug.endpoints.utils import valid_error

# TOOD; Move this to utils.py ?
def authorization_denied():
    return {}, 401

def make_endpoint_block(endpoint):
    block = {}

    if endpoint.specs['name']:
        block['name'] = endpoint.specs['name']

    if endpoint.specs['description']:
        block['description'] = endpoint.specs['description']

    operate = endpoint.specs.get('operate')
    if operate is not None:
        block['operate'] = 'item' if operate == Operate.ITEM else 'collection'

    if endpoint.specs['authentication']:
        block['authentication'] = True

    if endpoint.specs['request']:
        block['request'] = endpoint.specs['request']

    if endpoint.specs['response']:
        block['response'] = endpoint.specs['response']

    errors_block = {}
    for key, value in endpoint.specs['errors'].items():
        error_block = {}
        if value['name']:
            error_block['name'] = value['name']

        if value['description']:
            error_block['description'] = value['description']


        if value['specs']:
            error_block['value'] = value['specs']

        errors_block[key] = error_block

    if len(errors_block) > 0:
        block['errors'] = errors_block

    return block

class Endpoints:
    def __init__(self, name, title=None, summary=None, contact=None, license=None, version=None):

        self.flask = Flask(name)
        self.flask_cors = CORS(self.flask)

        self.title = title
        self.summary = summary

        self.contact = contact
        self.license = license

        self.version = version

        self.endpoints = []
        self.collections = {}

    def add_record(self, tag, specs):
        assert re.match(r"^[a-z]+(-[a-z]+)*$", tag), "invalid record name"
        validate_specs(specs.to_object())

        assert tag not in Record.records_map, "record with that name already exists"
        Record.records_map[tag] = specs

    def add_collection(self, tag, name=None, description=None):
        assert re.match(r"^[a-z]+(-[a-z]+)*$", tag), "invalid collection name"

        assert tag not in self.collections, "collection with that name already exists"
        self.collections[tag] = {
            'name': name,
            'description': description,
            'endpoints': []
        }

    def add_endpoint(self, endpoint):
        assert 'specs' in dir(endpoint), "not an endpoint"

        if endpoint.specs.get('collection'):
            name = endpoint.specs.get('collection')

            collection = self.collections.get(name)
            assert collection is not None, "collection does not exist (must be added first)"

            # Ensure uniqueness of the endpoint (path must be unique).
            for endpoint_ in collection['endpoints']:
                if endpoint.specs['path'] == endpoint_.specs['path']:
                   raise AssertionError("endpoint is not unique")

            collection['endpoints'].append(endpoint)
        else:
            # Ensure uniqueness of the endpoint (path must be unique).
            for endpoint_ in self.endpoints:
                if endpoint.specs['path'] == endpoint_.specs['path']:
                   raise AssertionError("endpoint is not unique")

            self.endpoints.append(endpoint)

        # Add route to Flask instance

        # TODO; Double-check the following.
        #
        # - Check must have at least one endpoint (collection or not)
        # - Check each collection must have at least one endpoint ?
        #

        def endpoint_function_maker(endpoint):
            def endpoint_function(*args, **kwargs):

                input_kwargs = {}

                # If the endpoint is "protected", we check for the token and
                # raise a 401 Unauthorized response.
                if endpoint.specs['authentication']:
                    # TODO; This is a quick and dirty implementation; to be
                    #       improved.
                    authorization_value = request.headers.get("Authorization")
                    if not authorization_value:
                        return authorization_denied()

                    try:
                        parts = authorization_value.split(" ")
                        assert len(parts) == 2
                        assert parts[0] == "Bearer"
                        token = parts[1]
                    except:
                        return authorization_denied()

                    input_kwargs['token'] = token

                # If this is a collection endpoint operating on the item level,
                # we read the item ID.
                item_id = kwargs.get("item_id")
                if item_id is not None:
                    input_kwargs['item'] = item_id


                has_body = request.content_length > 0
                is_body_json = None
                if has_body:
                    is_body_json = request.is_json
                json_body = None
                if is_body_json:
                    json_body = request.json

                document = None
                if endpoint.specs['request']:
                    if not has_body:
                        return json_body_expected()

                    if not is_body_json:
                        return body_not_json_format()

                    errors, warnings = [], []
                    document = document_to_object(json_body, endpoint.specs['request'], errors=errors, warnings=warnings)
                    if len(errors) > 0:
                        return json_body_specs_mismatch(errors, warnings)

                    input_kwargs['document'] = document

                else:
                    if has_body:
                        return no_json_body_expected()


                # If the endpoint has an adaptor, we take it into account and
                # transform the input arguments (note that the adaptor has
                # fixed signature and return a list of arguments to pass to the
                # actual endpoint function).
                adaptor = endpoint.specs.get('adaptor')
                adapted_input_args = None
                if adaptor is not None:
                    adapted_input_args = adaptor(**input_kwargs)

                try:
                    if not adapted_input_args:
                        value = endpoint(*input_kwargs.values())
                    else:
                        value = endpoint(*adapted_input_args)

                except EndpointError as e:
                    errors = endpoint.specs.get('errors')

                    if e.tag in errors:
                        error = errors[e.tag]

                        document = None
                        if error['specs']:
                            # Technically, we could check for the exception to
                            # have None for value when the error does not have
                            # a specs, but the object_to_document() will take
                            # care of it.

                            # assert e.value != None, "error didn't expect a value"

                            errors, warnings = [], []
                            document = object_to_document(e.value, error['specs'], errors=errors, warnings=warnings, no_dump=True)

                            if len(errors) > 0:
                                return invalid_error_specs_mismatch(errors, warnings)

                        return valid_error(e.tag, document, error['name'], error['description'])
                    else:
                        return invalid_error()
                except Exception as e:
                    return unhandled_error()

                if endpoint.specs['response']:
                    errors, warnings = [], []
                    document = object_to_document(value, endpoint.specs['response'], errors=errors, warnings=warnings)
                    if len(errors) > 0:
                        return invalid_response_specs_mismatch(errors, warnings)

                    return document
                else:
                    return ('', 204)

            # TODO; Remove this.
            def debug_endpoint_function(*args, **kwargs):
                import traceback

                try:
                    data = endpoint_function(*args, **kwargs)
                except Exception as e:
                    print(e)
                    # print(traceback.print_stack())
                    raise
                return data

            return debug_endpoint_function

        is_collection_endpoint = endpoint.specs.get('collection') is not None

        if not is_collection_endpoint:
            name = f"root/{endpoint.specs['path']}"
            path = f"/{endpoint.specs['path']}"
            function = endpoint_function_maker(endpoint)

            self.flask.add_url_rule(path, name, function, methods=('POST',))

        else:
            name = f"collection/{endpoint.specs['collection']}/{endpoint.specs['path']}"

            if endpoint.specs['operate'] == Operate.COLLECTION:
                path = f"/{endpoint.specs['collection']}/{endpoint.specs['path']}"
            elif endpoint.specs['operate'] == Operate.ITEM:
                path = f"/{endpoint.specs['collection']}/<item_id>/{endpoint.specs['path']}"

            function = endpoint_function_maker(endpoint)

            self.flask.add_url_rule(path, name, function, methods=('POST',))

    def add_expose_specs_endpoint(self, path='/specs', no_yaml=False):
        specs_obj = self.generate_specs(to_string=None)

        # TODO; Quick and dirty implementation, beautify this.
        if no_yaml:
            @self.flask.route(path, methods=['GET'])
            def json_specs():
                return specs_obj, 200, {'Content-Type': 'application/json'}
        else:
            specs_yaml_string = yaml.safe_dump(specs_obj, sort_keys=False)
            @self.flask.route(path, methods=['GET'])
            def yaml_specs():
                return specs_yaml_string, 200, {'Content-Type': 'text/vnd.yaml'}

    def add_shutdown_endpoint(self):
        # Code taken from Stackoverflow (turns out it's not necessary by the
        # unit tests; could be removed).
        @self.flask.route("/shutdown", methods=['GET'])
        def shutdown():
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func is None:
                raise RuntimeError('Not running werkzeug')
            shutdown_func()
            return "Shutting down..."

    def run(self, host='127.0.0.1', port=5000):
        self.flask.run(host, port)

    def generate_specs(self, to_string=True):

        block = {}
        block['standard'] = "https://www.byteplug.io/standards/easy-endpoints/1.0"

        # TODO; Early implementation; this is a quick and dumb implementation.
        if self.title:
            block['title'] = self.title

        if self.summary:
            block['summary'] = self.summary

        if self.contact:
            block['contact'] = self.contact

        if self.license:
            block['license'] = self.license

        if self.version:
            block['version'] = self.version

        # Generate 'records' block.
        records_block = {}
        for record, specs in Record.records_map.items():
            records_block[record] = specs.to_object()
        block['records'] = records_block

        # Generate 'endpoints' block.
        endpoints_block = {}
        for endpoint in self.endpoints:
            endpoints_block[endpoint.specs['path']] = make_endpoint_block(endpoint)

        if len(endpoints_block) > 0:
            block['endpoints'] = endpoints_block

        # Generate 'collections' block.
        collections_block = {}
        for key, value in self.collections.items():
            endpoints = value.get('endpoints')
            if len(endpoints) == 0:
                continue

            collection_block = {}
            if value['name']:
                collection_block['name'] = value['name']

            if value['description']:
                collection_block['description'] = value['description']

            endpoints_block = {}
            for endpoint in endpoints:
                endpoints_block[endpoint.specs['path']] = make_endpoint_block(endpoint)

            if len(endpoints_block) > 0:
                collection_block['endpoints'] = endpoints_block

            collections_block[key] = collection_block

        if len(collections_block) > 0:
            block['collections'] = collections_block

        if to_string:
            return yaml.safe_dump(block, sort_keys=False)
        else:
            return block
