# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, July 2022

def errors_to_json(errors):
    json = []
    for error in errors:
        item = {
            'path': error.path,
            'message': error.message
        }
        json.append(item)

    return json

def json_response(json, code):
    return json, code, {'Content-Type': 'application/json'}

def json_body_expected():
    json = {
        'kind': 'client-side-error',
        'code': 'json-body-expected',
        'name': "A JSON body was expected",
        'description': "This endpoint expected a JSON body in the HTTP request."
    }

    return json_response(json, 400)

def body_not_json_format():
    json = {
        'kind': 'client-side-error',
        'code': 'body-not-json-format',
        'name': "The body is not JSON format",
        'description': "The format of the body in the HTTP request must be JSON."
    }

    return json_response(json, 400)

def json_body_specs_mismatch(errors, warnings):
    json = {
        'kind': 'client-side-error',
        'code': 'json-body-specs-mismatch',
        'name': "The JSON body does not match the specs",
        'description': "The JSON body in the HTTP request does not match the specifications.",
        'errors': errors_to_json(errors),
        'warnings': errors_to_json(warnings)
    }

    return json_response(json, 400)

def no_json_body_expected():
    json = {
        'kind': 'client-side-error',
        'code': 'no-json-body-expected',
        'name': "No JSON body was expected",
        'description': "This endpoint did not expect a body in the HTTP request."
    }

    return json_response(json, 400)

def invalid_response_specs_mismatch(errors, warnings):
    json = {
        'kind': 'server-side-error',
        'code': 'invalid-response-specs-mismatch',
        'name': "Invalid returned response JSON body",
        'description': "The endpoint did not return a response JSON body matching its specifications.",
        'errors': errors_to_json(errors),
        'warnings': errors_to_json(warnings)
    }

    return json_response(json, 500)

def invalid_error():
    json = {
        'kind': 'server-side-error',
        'code': 'invalid-error',
        'name': "Invalid returned error",
        'description': "The endpoint returned an unexpected error (not listed in its specifications)."
    }

    return json_response(json, 500)

def invalid_error_specs_mismatch(errors, warnings):
    json = {
        'kind': 'server-side-error',
        'code': 'invalid-error-specs-mismatch',
        'name': "Invalid returned error JSON body",
        'description': "The endpoint did not return an error JSON body matching its specifications.",
        'errors': errors_to_json(errors),
        'warnings': errors_to_json(warnings)
    }

    return json_response(json, 500)

def unhandled_error():
    json = {
        'kind': 'server-side-error',
        'code': 'unhandled-error',
        'name': "Unhandled error",
        'description': "An unexpected and unhandled error occurred during the execution of the endpoint."
    }

    return json_response(json, 500)

def valid_error(tag, value, name=None, description=None):
    json = {
        'kind': 'error',
        'code': tag
    }

    if value is not None:
        json['value'] = value

    if name:
        json['name'] = name
    if description:
        json['description'] = description

    return json_response(json, 500)
