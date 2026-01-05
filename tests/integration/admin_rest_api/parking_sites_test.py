"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from http import HTTPStatus
from pathlib import Path
from typing import Generator
from unittest.mock import ANY

import pytest
from flask.testing import FlaskClient
from parkapi_sources.models import ParkAndRideType, ParkingSiteType

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input
from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.models import ParkingSite


def test_get_parking_site_by_id(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_site: ParkingSite,
) -> None:
    result = admin_api_test_client.get(
        '/api/admin/v1/parking-sites/1',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == EXISTING_PARKING_SITE_RESPONSE


def test_get_parking_site_by_uid(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_site: ParkingSite,
) -> None:
    result = admin_api_test_client.get(
        '/api/admin/v1/parking-sites/by-uid/demo-parking-site',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == EXISTING_PARKING_SITE_RESPONSE


def test_delete_get_parking_site_by_id(
    db: SQLAlchemy,
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_site: ParkingSite,
) -> None:
    result = admin_api_test_client.delete(
        '/api/admin/v1/parking-sites/1',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.NO_CONTENT
    assert db.session.get(ParkingSite, 1) is None


def test_delete_get_parking_site_by_uid(
    db: SQLAlchemy,
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    inserted_parking_site: ParkingSite,
) -> None:
    result = admin_api_test_client.delete(
        '/api/admin/v1/parking-sites/by-uid/demo-parking-site',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.NO_CONTENT
    assert db.session.get(ParkingSite, 1) is None


def test_upsert_parking_site_list(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-list',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-list'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == {
        'items': [PARKING_SITE_RESPONSE_ITEM],
        'errors': [
            {
                'source_uid': 'source',
                'message': 'Invalid parking site',
                'data': {
                    'code': 'field_errors',
                    'field_errors': {'type': {'code': 'required_field'}, 'uid': {'code': 'required_field'}},
                },
                'parking_site_uid': None,
            },
        ],
    }


def test_upsert_parking_site_list_legacy_fields(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-list',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-list-with-legacy-fields'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == {
        'items': [PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTIONS],
        'errors': [
            {
                'source_uid': 'source',
                'message': 'Invalid parking site',
                'data': {
                    'code': 'field_errors',
                    'field_errors': {'type': {'code': 'required_field'}, 'uid': {'code': 'required_field'}},
                },
                'parking_site_uid': None,
            },
        ],
    }


def test_upsert_parking_site_item(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == PARKING_SITE_RESPONSE_ITEM


def test_upsert_parking_site_item_with_legacy_fields(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item-with-legacy-fields'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTIONS


def test_upsert_parking_site_item_with_legacy_restricted_to(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item-with-restricted-to'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTED_TO


def test_upsert_parking_site_list_with_relations(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item-with-relations'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == PARKING_SITE_RESPONSE_ITEM_WITH_RELATIONS


@pytest.fixture()
def parking_site_patch(flask_app: App) -> Generator[None, None, None]:
    json_file_path = Path(flask_app.config.get('PARKING_SITE_PATCH_DIR'), 'source.json')
    json_file_path.parent.mkdir(parents=True, exist_ok=True)

    patch_data = {
        'items': [
            {
                'uid': '12717250',
                'type': 'UNDERGROUND',
                'park_and_ride_type': ['TRAM'],
                'external_identifiers': [{'type': 'DHID', 'value': 'de:08111:6027:1:1'}],
            },
            {
                'uid': '12717432',
                'type': 'UNDERGROUND',
            },
        ],
    }

    with json_file_path.open('w') as json_file:
        json_file.write(json.dumps(patch_data))

    yield

    json_file_path.unlink()


def test_upsert_parking_site_item_with_patch(
    db: SQLAlchemy,
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
    parking_site_patch: None,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item'),
    )

    assert result.status_code == HTTPStatus.OK

    parking_site = db.session.get(ParkingSite, 1)

    assert parking_site.park_and_ride_type == [ParkAndRideType.TRAM]
    assert parking_site.type == ParkingSiteType.UNDERGROUND
    assert len(parking_site.external_identifiers) == 1


def test_upsert_parking_site_list_with_restricted_to(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/upsert-item',
        auth=('source', 'test'),
        json=load_admin_client_request_input('parking-site-item-with-restricted-to'),
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json == PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTED_TO


def test_generate_duplicates_simple(
    multi_source_parking_site_test_data: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/generate',
        auth=('dev', 'test'),
        json={
            'radius': 25000,
        },
    )

    assert result.status_code == 200
    duplicates = result.json['items']

    # As we just output duplicates where each site is at another source, and we have three sources, we expect
    # two duplicates pairs, therefor four datasets
    assert len(duplicates) == 4


def test_generate_duplicates_source_uids(
    multi_source_parking_site_test_data: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/generate',
        auth=('dev', 'test'),
        json={
            'radius': 25000,
            'source_uids': ['source-1'],
        },
    )

    assert result.status_code == 200
    duplicates = result.json['items']

    # As we just output duplicates where each site is at another source, and we have three sources, filtered to one,
    # we expect two duplicates pairs, because the other pair is between source-2 and source-3
    assert len(duplicates) == 2


def test_reset_duplicates_source_uids(admin_api_test_client: FlaskClient, db: SQLAlchemy) -> None:
    parking_site_1 = get_parking_site(source=get_source(), original_uid='test-1')
    db.session.add(parking_site_1)
    parking_site_2 = get_parking_site(source=get_source(), original_uid='test-2')
    db.session.add(parking_site_2)
    parking_site_2.duplicate_of_parking_site_id = 1
    db.session.commit()

    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/reset',
        auth=('dev', 'test'),
        json={},
    )

    assert result.status_code == 204
    assert parking_site_2.duplicate_of_parking_site_id is None


def test_filter_reset_duplicates_source_uids(admin_api_test_client: FlaskClient, db: SQLAlchemy) -> None:
    parking_site_1 = get_parking_site(source=get_source(), original_uid='test-1')
    db.session.add(parking_site_1)
    parking_site_2 = get_parking_site(source=get_source(), original_uid='test-2')
    db.session.add(parking_site_2)
    parking_site_2.duplicate_of_parking_site_id = 1
    db.session.commit()

    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/reset',
        auth=('dev', 'test'),
        json={'purpose': 'BIKE'},
    )

    assert result.status_code == 204
    assert parking_site_2.duplicate_of_parking_site_id == 1


EXISTING_PARKING_SITE_RESPONSE = {
    'source_id': 2,
    'original_uid': 'demo-parking-site',
    'name': 'Demo Parking Site',
    'operator_name': 'Demo Operator',
    'address': 'Demo Address, Demo City',
    'description': 'Demo Description',
    'type': 'CAR_PARK',
    'purpose': 'CAR',
    'has_fee': False,
    'has_realtime_data': False,
    'static_data_updated_at': ANY,
    'lat': '50.0000000',
    'lon': '10.0000000',
    'capacity': 100,
    'opening_hours': 'Mo-Su 08:00-18:00',
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
}


PARKING_SITE_RESPONSE_ITEM = {
    'source_id': 1,
    'original_uid': '12717250',
    'name': 'Parkhaus Hofdiener',
    'operator_name': 'PBW Parkraumgesellschaft Baden-W\u00fcrttenberg mbH',
    'address': 'Schellingstra\u00dfe',
    'type': 'ON_STREET',
    'purpose': 'CAR',
    'has_realtime_data': True,
    'static_data_updated_at': '2023-12-12T12:27:54Z',
    'realtime_data_updated_at': '2025-06-24T11:54:45Z',
    'realtime_opening_status': 'OPEN',
    'lat': '54.0300500',
    'lon': '5.1269600',
    'capacity': 158,
    'realtime_capacity': 158,
    'realtime_free_capacity': 15,
    'opening_hours': '24/7',
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
}


PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTIONS = {
    **PARKING_SITE_RESPONSE_ITEM,
    'capacity_disabled': 11,
    'realtime_capacity_disabled': 10,
    'realtime_free_capacity_disabled': 2,
    'restricted_to': [],
    'restrictions': [
        {
            'capacity': 11,
            'realtime_capacity': 10,
            'realtime_free_capacity': 2,
            'type': 'DISABLED',
        },
    ],
}


PARKING_SITE_RESPONSE_ITEM_WITH_RESTRICTED_TO = {
    **PARKING_SITE_RESPONSE_ITEM,
    'restricted_to': [
        {
            'max_stay': 'PT2H',
        },
        {
            'max_stay': 'PT12H',
            'type': 'DISABLED',
        },
    ],
    'restrictions': [
        {
            'max_stay': 'PT2H',
        },
        {
            'max_stay': 'PT12H',
            'type': 'DISABLED',
        },
    ],
}


PARKING_SITE_RESPONSE_ITEM_WITH_RELATIONS = {
    **PARKING_SITE_RESPONSE_ITEM,
    'external_identifiers': [
        {
            'type': 'OSM',
            'value': '123456789',
        },
    ],
    'capacity_disabled': 11,
    'realtime_capacity_disabled': 10,
    'realtime_free_capacity_disabled': 2,
    'restricted_to': [
        {
            'max_stay': 'PT2H',
        },
    ],
    'restrictions': [
        {
            'max_stay': 'PT2H',
        },
        {
            'capacity': 11,
            'max_stay': 'PT12H',
            'realtime_capacity': 10,
            'realtime_free_capacity': 2,
            'type': 'DISABLED',
        },
    ],
}
