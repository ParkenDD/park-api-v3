"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

import mercantile
import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time
from mapbox_vector_tile import decode
from parkapi_sources.models.enums import PurposeType

from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy

# The realtime data of the test parking sites was last updated at this point in time.
REALTIME_DATA_UPDATED_AT = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# Tile at zoom 12 which contains the default test parking site
TILE = mercantile.tile(10.0, 50.0, 12)
TILE_PATH = f'/api/public/v3/tiles/{TILE.z}/{TILE.x}/{TILE.y}.mvt'


@pytest.fixture
def parking_sites(db: SQLAlchemy) -> None:
    source = get_source()
    car_parking_site = get_parking_site(
        source=source,
        has_realtime_data=True,
        realtime_data_updated_at=REALTIME_DATA_UPDATED_AT,
        realtime_free_capacity=42,
    )
    bike_parking_site = get_parking_site(
        source=source,
        original_uid='bike',
        name='Bike Parking',
        purpose=PurposeType.BIKE,
        capacity=20,
        lat=Decimal('50.001'),
        lon=Decimal('10.001'),
    )
    duplicate_parking_site = get_parking_site(
        source=source,
        original_uid='duplicate',
        lat=Decimal('50.002'),
        lon=Decimal('10.002'),
        duplicate_of_parking_site=car_parking_site,
    )
    db.session.add_all([car_parking_site, bike_parking_site, duplicate_parking_site])
    db.session.commit()


def get_features(public_api_test_client: FlaskClient, path: str) -> list[dict]:
    response = public_api_test_client.get(path=path)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-protobuf'

    layers = decode(response.data)
    return sorted(layers['parking_sites']['features'], key=lambda feature: feature['properties']['id'])


@freeze_time('2025-01-01 12:10:00')
def test_get_tile(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, TILE_PATH)

    assert [feature['properties'] for feature in features] == [
        {'id': 1, 'name': 'Demo Parking Site', 'purpose': 'CAR', 'capacity': 100, 'free_capacity': 42},
        {'id': 2, 'name': 'Bike Parking', 'purpose': 'BIKE', 'capacity': 20},
    ]


@freeze_time('2025-01-02 13:00:00')
def test_get_tile_outdated_realtime_data(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    # More than 24 hours after the last realtime update, which is above the push threshold
    features = get_features(public_api_test_client, TILE_PATH)

    assert 'free_capacity' not in features[0]['properties']


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_with_duplicates(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?ignore_duplicates=false')

    assert [feature['properties']['id'] for feature in features] == [1, 2, 3]


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_by_purpose(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?purpose=BIKE')

    assert [feature['properties']['id'] for feature in features] == [2]


def test_get_tile_zoomed_out(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    tile = mercantile.tile(10.0, 50.0, 7)

    assert get_features(public_api_test_client, f'/api/public/v3/tiles/{tile.z}/{tile.x}/{tile.y}.mvt') == []
