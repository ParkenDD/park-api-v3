"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from http import HTTPStatus
from unittest.mock import ANY

from flask.testing import FlaskClient

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.models import ParkingSpot


def test_get_parking_spot_by_id(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_spot: ParkingSpot,
) -> None:
    result = admin_api_test_client.get(
        '/api/admin/v1/parking-spots/1',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json == EXISTING_PARKING_SPOT_RESPONSE


def test_get_parking_spot_by_uid(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_spot: ParkingSpot,
) -> None:
    result = admin_api_test_client.get(
        '/api/admin/v1/parking-spots/by-uid/demo-parking-spot',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == EXISTING_PARKING_SPOT_RESPONSE


def test_delete_parking_spot_by_id(
    db: SQLAlchemy,
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_spot: ParkingSpot,
) -> None:
    result = admin_api_test_client.delete(
        '/api/admin/v1/parking-spots/1',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )
    assert result.status_code == HTTPStatus.NO_CONTENT
    assert db.session.get(ParkingSpot, 1) is None


def test_delete_parking_spot_by_uid(
    db: SQLAlchemy,
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_spot: ParkingSpot,
) -> None:
    result = admin_api_test_client.delete(
        '/api/admin/v1/parking-spots/by-uid/demo-parking-spot',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )
    assert result.status_code == HTTPStatus.NO_CONTENT
    assert db.session.get(ParkingSpot, 1) is None


def test_create_parking_spot(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-spots/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot'),
    )

    assert result.status_code == HTTPStatus.CREATED
    assert result.json == PARKING_SPOT_RESPONSE


def test_create_parking_spot_legacy_endpoint(
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
        '/api/admin/v1/parking-spots/upsert-item',
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


def test_create_parking_spot_with_relations(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-spots/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot-with-relations'),
    )

    assert result.status_code == HTTPStatus.CREATED
    assert result.json == PARKING_SPOT_WITH_RELATIONS_RESPONSE


def test_create_parking_spot_with_restricted_to(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-spots/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-spot-with-restricted-to'),
    )

    assert result.status_code == HTTPStatus.CREATED
    assert result.json == PARKING_SPOT_WITH_RESTRICTED_TO_RESPONSE


EXISTING_PARKING_SPOT_RESPONSE = {
    'source_id': 2,
    'original_uid': 'demo-parking-spot',
    'name': 'Test',
    'lat': '50.0000000',
    'lon': '10.0000000',
    'geojson': {
        'type': 'Polygon',
        'coordinates': [[[50.1, 10.1], [50.2, 10.1], [50.2, 10.2], [50.1, 10.2], [50.1, 10.1]]],
    },
    'purpose': 'CAR',
    'realtime_status': 'AVAILABLE',
    'static_data_updated_at': ANY,
    'realtime_data_updated_at': ANY,
    'has_realtime_data': True,
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
}


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
}


PARKING_SPOT_WITH_RELATIONS_RESPONSE = {
    **PARKING_SPOT_RESPONSE,
    'restrictions': [{'type': 'DISABLED'}],
    'restricted_to': [{'type': 'DISABLED'}],
}


PARKING_SPOT_WITH_RESTRICTED_TO_RESPONSE = PARKING_SPOT_WITH_RELATIONS_RESPONSE
