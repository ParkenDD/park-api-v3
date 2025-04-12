"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.testing import FlaskClient

from tests.integration.public_rest_api.parking_site.parking_site_responses import (
    PARKING_SITE_ITEM_RESPONSE,
    PARKING_SITE_LIST_RESPONSE,
)


def test_get_parking_site_list(public_api_test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-sites')

    assert response.status_code == 200
    assert response.json == PARKING_SITE_LIST_RESPONSE


def test_get_parking_site_item(public_api_test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-sites/1')

    assert response.status_code == 200
    assert response.json == PARKING_SITE_ITEM_RESPONSE
