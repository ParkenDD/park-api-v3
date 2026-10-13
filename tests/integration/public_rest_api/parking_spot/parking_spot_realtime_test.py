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
from webapp.dependencies import dependencies

# The realtime data of the test parking spot was last updated at this point in time.
REALTIME_DATA_UPDATED_AT = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

ITEM_PATH = '/api/public/v3/parking-spots/1'
LIST_PATH = '/api/public/v3/parking-spots'


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


@pytest.fixture
def pull_source(flask_app, monkeypatch: pytest.MonkeyPatch) -> None:
    # The test source is a generic source and therefore a push source, so we flag it as pull source explicitly.
    monkeypatch.setattr(dependencies.get_generic_import_service(), 'is_pull_source', lambda source_uid: True)


def assert_realtime_data_kept(data: dict) -> None:
    assert data['has_realtime_data'] is True
    assert_realtime_fields(data)


def assert_realtime_fields(data: dict) -> None:
    assert data['realtime_data_updated_at'] == '2025-01-01T12:00:00Z'
    assert data['realtime_status'] == 'AVAILABLE'


def assert_realtime_data_outdated(data: dict) -> None:
    # Outdated realtime data is flagged via has_realtime_data, but no attributes are removed
    assert data['has_realtime_data'] is False
    assert_realtime_fields(data)


@freeze_time('2025-01-01 12:10:00')
def test_pull_realtime_data_fresh(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    # 10 minutes after the last realtime update, which is below the 30 minute pull threshold
    response = public_api_test_client.get(path=ITEM_PATH)

    assert response.status_code == 200
    assert_realtime_data_kept(response.json)


@freeze_time('2025-01-01 12:40:00')
def test_pull_realtime_data_outdated(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    # 40 minutes after the last realtime update, which is above the 30 minute pull threshold
    response = public_api_test_client.get(path=ITEM_PATH)

    assert response.status_code == 200
    assert_realtime_data_outdated(response.json)


@freeze_time('2025-01-01 12:40:00')
def test_pull_realtime_data_outdated_in_list(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    response = public_api_test_client.get(path=LIST_PATH)

    assert response.status_code == 200
    assert_realtime_data_outdated(response.json['items'][0])


@freeze_time('2025-01-01 12:40:00')
def test_pull_realtime_data_outdated_calculation_disabled(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    # calculate_has_realtime_data=false skips the outdating calculation, so the raw realtime data is kept
    response = public_api_test_client.get(path=f'{ITEM_PATH}?calculate_has_realtime_data=false')

    assert response.status_code == 200
    assert_realtime_data_kept(response.json)


@freeze_time('2025-01-01 12:40:00')
def test_pull_realtime_data_outdated_calculation_disabled_in_list(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    response = public_api_test_client.get(path=f'{LIST_PATH}?calculate_has_realtime_data=false')

    assert response.status_code == 200
    assert_realtime_data_kept(response.json['items'][0])


@freeze_time('2025-01-01 12:40:00')
def test_pull_realtime_data_outdated_calculation_enabled_explicitly(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
    pull_source: None,
) -> None:
    # calculate_has_realtime_data=true is the default behaviour, so outdated realtime data is still flagged
    response = public_api_test_client.get(path=f'{ITEM_PATH}?calculate_has_realtime_data=true')

    assert response.status_code == 200
    assert_realtime_data_outdated(response.json)


@freeze_time('2025-01-02 11:00:00')
def test_push_realtime_data_fresh(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    # 23 hours after the last realtime update, which is below the 24 hour push threshold
    response = public_api_test_client.get(path=ITEM_PATH)

    assert response.status_code == 200
    assert_realtime_data_kept(response.json)


@freeze_time('2025-01-02 13:00:00')
def test_push_realtime_data_outdated(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    # 25 hours after the last realtime update, which is above the 24 hour push threshold
    response = public_api_test_client.get(path=ITEM_PATH)

    assert response.status_code == 200
    assert_realtime_data_outdated(response.json)


@freeze_time('2025-01-02 13:00:00')
def test_push_realtime_data_outdated_in_list(public_api_test_client: FlaskClient, realtime_parking_spot: None) -> None:
    response = public_api_test_client.get(path=LIST_PATH)

    assert response.status_code == 200
    assert_realtime_data_outdated(response.json['items'][0])


@freeze_time('2025-01-02 13:00:00')
def test_push_realtime_data_outdated_calculation_disabled(
    public_api_test_client: FlaskClient,
    realtime_parking_spot: None,
) -> None:
    response = public_api_test_client.get(path=f'{ITEM_PATH}?calculate_has_realtime_data=false')

    assert response.status_code == 200
    assert_realtime_data_kept(response.json)
