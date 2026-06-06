"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time
from parkapi_sources.models.enums import OpeningStatus

from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy

# The realtime data of the test parking site was last updated at this point in time.
REALTIME_DATA_UPDATED_AT = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def realtime_parking_site(db: SQLAlchemy) -> None:
    parking_site = get_parking_site(
        source=get_source(),
        has_realtime_data=True,
        realtime_data_updated_at=REALTIME_DATA_UPDATED_AT,
        realtime_opening_status=OpeningStatus.OPEN,
        realtime_capacity=100,
        realtime_free_capacity=42,
    )
    db.session.add(parking_site)
    db.session.commit()


@freeze_time('2025-01-01 12:10:00')
def test_realtime_data_fresh(public_api_test_client: FlaskClient, realtime_parking_site: None) -> None:
    # 10 minutes after the last realtime update, which is below the 15 minute threshold, so realtime data is kept.
    response = public_api_test_client.get(path='/api/public/v3/parking-sites/1')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is True
    assert response.json['realtime_data_updated_at'] == '2025-01-01T12:00:00Z'
    assert response.json['realtime_capacity'] == 100
    assert response.json['realtime_free_capacity'] == 42


@freeze_time('2025-01-01 12:20:00')
def test_realtime_data_outdated(public_api_test_client: FlaskClient, realtime_parking_site: None) -> None:
    # 20 minutes after the last realtime update, which is above the 15 minute threshold, so realtime data is dropped.
    response = public_api_test_client.get(path='/api/public/v3/parking-sites/1')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is False
    assert not any(key.startswith('realtime_') for key in response.json)


@freeze_time('2025-01-01 12:20:00')
def test_realtime_data_outdated_in_list(public_api_test_client: FlaskClient, realtime_parking_site: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-sites')

    assert response.status_code == 200
    item = response.json['items'][0]
    assert item['has_realtime_data'] is False
    assert not any(key.startswith('realtime_') for key in item)
