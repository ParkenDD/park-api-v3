"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.testing import FlaskClient

from tests.integration.public_rest_api.parking_spot.parking_spot_responses import (
    PARKING_SPOT_ITEM_RESPONSE,
    PARKING_SPOT_LIST_RESPONSE,
)


def test_get_parking_spot_list(test_client: FlaskClient, multi_source_parking_spot_test_data: None) -> None:
    response = test_client.get(path='/api/public/v3/parking-spots')

    assert response.json['items'][1] == PARKING_SPOT_LIST_RESPONSE['items'][1]
    assert response.status_code == 200
    assert response.json == PARKING_SPOT_LIST_RESPONSE


def test_get_parking_spot_item(test_client: FlaskClient, multi_source_parking_spot_test_data: None) -> None:
    response = test_client.get(path='/api/public/v3/parking-spots/1')

    assert response.status_code == 200
    assert response.json == PARKING_SPOT_ITEM_RESPONSE
