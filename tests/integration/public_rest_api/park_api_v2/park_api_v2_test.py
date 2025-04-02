"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.testing import FlaskClient

from tests.integration.public_rest_api.park_api_v2.park_api_v2_responses import (
    PARK_API_V2_LOTS_RESPONSE,
    PARK_API_V2_POOL_RESPONSE,
)


def test_get_v1_pool(test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = test_client.get(path='/api/public/v2/pools/source-1/')
    assert response.status_code == 200
    assert response.json == PARK_API_V2_POOL_RESPONSE


def test_get_v1_lots(test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = test_client.get(path='/api/public/v2/lots/')

    assert response.status_code == 200
    assert response.json == PARK_API_V2_LOTS_RESPONSE
