"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time
from parkapi_sources.models.enums import ParkingSpotStatus

from tests.model_generator.parking_spot import get_parking_spot
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy

# The realtime data of the test parking spot was last updated at this point in time.
REALTIME_DATA_UPDATED_AT = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def realtime_parking_spot(db: SQLAlchemy) -> None:
    parking_spot = get_parking_spot(
        source=get_source(),
        has_realtime_data=True,
        realtime_data_updated_at=REALTIME_DATA_UPDATED_AT,
        realtime_status=ParkingSpotStatus.AVAILABLE,
    )
    db.session.add(parking_spot)
    db.session.commit()


@freeze_time('2025-01-01 12:10:00')
def test_realtime_data_fresh(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    # 10 minutes after the last realtime update, which is below the 30 minute threshold, so realtime data is kept.
    response = public_api_test_client.get(path='/api/public/v3/parking-spots/1')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is True
    assert response.json['realtime_data_updated_at'] == '2025-01-01T12:00:00Z'
    assert response.json['realtime_status'] == 'AVAILABLE'


@freeze_time('2025-01-01 12:40:00')
def test_realtime_data_outdated(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    # 40 minutes after the last realtime update, which is above the 30 minute threshold, so realtime data is dropped.
    response = public_api_test_client.get(path='/api/public/v3/parking-spots/1')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is False
    assert not any(key.startswith('realtime_') for key in response.json)


@freeze_time('2025-01-01 12:40:00')
def test_realtime_data_outdated_in_list(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-spots')

    assert response.status_code == 200
    item = response.json['items'][0]
    assert item['has_realtime_data'] is False
    assert not any(key.startswith('realtime_') for key in item)


@freeze_time('2025-01-01 12:40:00')
def test_realtime_data_outdated_calculation_disabled(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
) -> None:
    # 40 minutes after the last realtime update, but calculate_has_realtime_data=false skips the outdating
    # calculation, so the raw has_realtime_data and its realtime fields are kept.
    response = public_api_test_client.get(path='/api/public/v3/parking-spots/1?calculate_has_realtime_data=false')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is True
    assert response.json['realtime_data_updated_at'] == '2025-01-01T12:00:00Z'
    assert response.json['realtime_status'] == 'AVAILABLE'


@freeze_time('2025-01-01 12:40:00')
def test_realtime_data_outdated_calculation_disabled_in_list(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
) -> None:
    response = public_api_test_client.get(path='/api/public/v3/parking-spots?calculate_has_realtime_data=false')

    assert response.status_code == 200
    item = response.json['items'][0]
    assert item['has_realtime_data'] is True
    assert item['realtime_status'] == 'AVAILABLE'


@freeze_time('2025-01-01 12:40:00')
def test_realtime_data_outdated_calculation_enabled_explicitly(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
) -> None:
    # calculate_has_realtime_data=true is the default behaviour, so outdated realtime data is still dropped.
    response = public_api_test_client.get(path='/api/public/v3/parking-spots/1?calculate_has_realtime_data=true')

    assert response.status_code == 200
    assert response.json['has_realtime_data'] is False
    assert not any(key.startswith('realtime_') for key in response.json)
