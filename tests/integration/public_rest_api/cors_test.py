"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest
from flask import Flask
from flask.testing import FlaskClient

PUBLIC_PATHS = [
    '/api/public/v3/parking-sites',
    '/api/public/v3/tiles/12/2161/1406.mvt',
]


@pytest.mark.parametrize('path', PUBLIC_PATHS)
def test_public_api_without_cors(public_api_test_client: FlaskClient, path: str) -> None:
    response = public_api_test_client.get(path=path)

    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' not in response.headers


@pytest.mark.parametrize('path', PUBLIC_PATHS)
def test_public_api_with_cors_allow_all(flask_app: Flask, public_api_test_client: FlaskClient, path: str) -> None:
    flask_app.config['CORS_ALLOW_ALL'] = True

    response = public_api_test_client.get(path=path)

    assert response.status_code == 200
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_public_api_error_with_cors_allow_all(flask_app: Flask, test_client: FlaskClient) -> None:
    flask_app.config['CORS_ALLOW_ALL'] = True

    # Error responses are not part of the OpenAPI documentation, so this uses the client without response validation
    response = test_client.get(path='/api/public/v3/tiles/12/2161/1406.mvt?purpose=INVALID')

    assert response.status_code == 400
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_admin_api_with_cors_allow_all(flask_app: Flask, test_client: FlaskClient) -> None:
    flask_app.config['CORS_ALLOW_ALL'] = True

    response = test_client.get(path='/api/admin/v1/parking-sites')

    assert 'Access-Control-Allow-Origin' not in response.headers
