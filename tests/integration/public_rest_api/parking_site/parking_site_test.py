"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from flask.testing import FlaskClient

from tests.integration.public_rest_api.parking_site.parking_site_responses import (
    PARKING_SITE_ITEM_RESPONSE,
    PARKING_SITE_LIST_RESPONSE,
)
from tests.model_generator.parking_site import get_parking_site_by_counter
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy


def test_get_parking_site_list(public_api_test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-sites')

    assert response.status_code == 200
    assert response.json == PARKING_SITE_LIST_RESPONSE


def test_get_parking_site_item(public_api_test_client: FlaskClient, multi_source_parking_site_test_data: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-sites/1')

    assert response.status_code == 200
    assert response.json == PARKING_SITE_ITEM_RESPONSE


def test_get_parking_site_list_modified_since(public_api_test_client: FlaskClient, db: SQLAlchemy) -> None:
    source = get_source()

    db.session.add(
        get_parking_site_by_counter(counter=1, source=source, modified_at=datetime(2025, 1, 1, tzinfo=timezone.utc)),
    )
    db.session.add(
        get_parking_site_by_counter(counter=2, source=source, modified_at=datetime(2025, 3, 1, tzinfo=timezone.utc)),
    )
    db.session.add(
        get_parking_site_by_counter(counter=3, source=source, modified_at=datetime(2025, 5, 1, tzinfo=timezone.utc)),
    )
    db.session.commit()

    response = public_api_test_client.get(
        path='/api/public/v3/parking-sites',
        query_string={'modified_since': '2025-03-01T00:00:00Z'},
    )

    assert response.status_code == 200
    assert sorted(item['original_uid'] for item in response.json['items']) == [
        'demo-parking-site-2',
        'demo-parking-site-3',
    ]
