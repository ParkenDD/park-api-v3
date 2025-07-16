"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input


@pytest.fixture
def admin_api_test_client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    with flask_app.test_client(openapi_realm='admin') as client:
        yield client


@pytest.fixture
def rest_enabled_source(admin_api_test_client: FlaskClient) -> None:
    admin_api_test_client.post(
        '/api/admin/v1/sources',
        auth=('dev', 'test'),
        json=load_admin_client_request_input('source'),
    )
