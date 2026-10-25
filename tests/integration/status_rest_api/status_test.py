"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Flask
from flask.testing import FlaskClient
from parkapi_sources.version import __version__ as parkapi_sources_version


def test_root_status_without_project_version(test_client: FlaskClient) -> None:
    response = test_client.get(path='/')

    assert response.status_code == 200
    assert response.json['version'] == 'dev'
    assert response.json['parkapi_sources_version'] == parkapi_sources_version


def test_root_status_with_project_version(flask_app: Flask, test_client: FlaskClient) -> None:
    flask_app.config['PROJECT_VERSION'] = '1.2.3'

    response = test_client.get(path='/')

    assert response.status_code == 200
    assert response.json['version'] == '1.2.3'
