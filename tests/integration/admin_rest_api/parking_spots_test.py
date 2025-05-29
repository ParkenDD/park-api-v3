"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from http import HTTPStatus
from unittest.mock import ANY

from flask.testing import FlaskClient

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input


def test_create_parking_spot(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-spots',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )

    assert result.status_code == HTTPStatus.CREATED
    assert result.json == PARKING_SPOT_RESPONSE


def test_update_parking_spot(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    admin_api_test_client.post(
        '/api/admin/v1/parking-spots',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )

    parking_spot_data = load_admin_client_request_input('parking-spot')
    parking_spot_data['name'] = 'Updated Parking Spot'
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-spots',
        auth=('source', 'test'),
        json=parking_spot_data,
    )

    assert result.status_code == HTTPStatus.OK
    expected_response = deepcopy(PARKING_SPOT_RESPONSE)
    expected_response['name'] = 'Updated Parking Spot'
    assert result.json == expected_response


PARKING_SPOT_RESPONSE = {
    'source_id': 1,
    'original_uid': 'demo-parking-spot',
    'name': 'A1 4',
    'type': 'ON_STREET',
    'address': 'A1 4, 68159 Mannheim',
    'lat': '49.4853810',
    'lon': '8.4628792',
    'purpose': 'CAR',
    'realtime_status': 'TAKEN',
    'static_data_updated_at': '2025-05-20T11:55:33Z',
    'realtime_data_updated_at': '2025-05-20T11:55:33Z',
    'has_realtime_data': True,
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
    'restricted_to': [{'type': 'DISABLED'}],
}
