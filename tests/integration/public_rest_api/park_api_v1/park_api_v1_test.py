"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.testing import FlaskClient

from tests.integration.public_rest_api.park_api_v1.park_api_v1_responses import (
    PARK_API_V1_INDEX_RESPONSE,
    PARK_API_V1_POOL_RESPONSE,
)


def test_get_v1_index(test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = test_client.get(path='/api/public/v1')

    assert response.status_code == 200
    assert response.json == PARK_API_V1_INDEX_RESPONSE


def test_get_v1_pool(test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = test_client.get(path='/api/public/v1/source-1')

    assert response.status_code == 200
    assert response.json == PARK_API_V1_POOL_RESPONSE
