"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import make_response


def empty_json_response():
    response = make_response('')
    response.mimetype = 'application/json'
    return response
