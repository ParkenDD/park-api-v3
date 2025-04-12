"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def public_api_test_client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    with flask_app.test_client(openapi_realm='public') as client:
        yield client
