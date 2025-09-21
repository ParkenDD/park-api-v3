"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from http import HTTPStatus
from unittest.mock import ANY

from flask.testing import FlaskClient

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input
from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy


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
