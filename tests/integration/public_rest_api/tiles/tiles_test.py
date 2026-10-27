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
from parkapi_sources.models.enums import ParkingSiteType, PurposeType

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
    other_source = get_source(uid='other-source')
    bike_parking_site = get_parking_site(
        source=other_source,
        original_uid='bike',
        name='Bike Parking',
        purpose=PurposeType.BIKE,
        type=ParkingSiteType.STANDS,
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


def get_features(public_api_test_client: FlaskClient, path: str, layer: str = 'parking_sites') -> list[dict]:
    response = public_api_test_client.get(path=path)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-protobuf'

    layers = decode(response.data)
    return sorted(layers[layer]['features'], key=lambda feature: feature['properties']['id'])


def get_square(lon: float, lat: float, size: float) -> dict:
    return {
        'type': 'Polygon',
        'coordinates': [
            [[lon, lat], [lon + size, lat], [lon + size, lat + size], [lon, lat + size], [lon, lat]],
        ],
    }


# Tile at zoom 14 which contains the parking sites with geometries
GEOMETRY_TILE = mercantile.tile(10.0, 50.0, 14)
GEOMETRY_TILE_PATH = f'/api/public/v3/tiles/{GEOMETRY_TILE.z}/{GEOMETRY_TILE.x}/{GEOMETRY_TILE.y}.mvt'


@pytest.fixture
def parking_sites_with_geometries(db: SQLAlchemy) -> None:
    source = get_source()
    bounds = mercantile.bounds(GEOMETRY_TILE)

    polygon_parking_site = get_parking_site(source=source, original_uid='polygon')
    polygon_parking_site.geojson = get_square(10.0, 50.0, 0.0005)

    line_parking_site = get_parking_site(
        source=source,
        original_uid='line',
        lat=Decimal('50.001'),
        lon=Decimal('10.001'),
    )
    line_parking_site.geojson = {'type': 'LineString', 'coordinates': [[10.001, 50.001], [10.002, 50.001]]}

    # The point is outside of the tile, but the polygon reaches into it
    outside_parking_site = get_parking_site(
        source=source,
        original_uid='outside',
        lat=Decimal(str(bounds.south - 0.001)),
        lon=Decimal(str(bounds.west - 0.001)),
    )
    outside_parking_site.geojson = get_square(bounds.west - 0.001, bounds.south - 0.001, 0.002)

    point_only_parking_site = get_parking_site(
        source=source,
        original_uid='point-only',
        lat=Decimal('50.002'),
        lon=Decimal('10.002'),
    )

    broken_parking_site = get_parking_site(
        source=source,
        original_uid='broken',
        lat=Decimal('50.003'),
        lon=Decimal('10.003'),
    )
    broken_parking_site.geojson = {'type': 'Polygon', 'coordinates': 'broken'}

    db.session.add_all([
        polygon_parking_site,
        line_parking_site,
        outside_parking_site,
        point_only_parking_site,
        broken_parking_site,
    ])
    db.session.commit()


@freeze_time('2025-01-01 12:10:00')
def test_get_tile(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, TILE_PATH)

    assert [feature['properties'] for feature in features] == [
        {
            'id': 1,
            'name': 'Demo Parking Site',
            'purpose': 'CAR',
            'type': 'CAR_PARK',
            'capacity': 100,
            'free_capacity': 42,
        },
        {'id': 2, 'name': 'Bike Parking', 'purpose': 'BIKE', 'type': 'STANDS', 'capacity': 20},
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


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_by_type(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?types=STANDS')

    assert [feature['properties']['id'] for feature in features] == [2]


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_by_multiple_types(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?types=CAR_PARK,STANDS')

    assert [feature['properties']['id'] for feature in features] == [1, 2]


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_by_source_uids(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?source_uids=other-source')

    assert [feature['properties']['id'] for feature in features] == [2]


@freeze_time('2025-01-01 12:10:00')
def test_get_tile_by_multiple_source_uids(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    features = get_features(public_api_test_client, f'{TILE_PATH}?source_uids=source,other-source')

    assert [feature['properties']['id'] for feature in features] == [1, 2]


def test_get_tile_zoomed_out(public_api_test_client: FlaskClient, parking_sites: None) -> None:
    tile = mercantile.tile(10.0, 50.0, 7)

    assert get_features(public_api_test_client, f'/api/public/v3/tiles/{tile.z}/{tile.x}/{tile.y}.mvt') == []


def test_get_tile_geometries(public_api_test_client: FlaskClient, parking_sites_with_geometries: None) -> None:
    features = get_features(public_api_test_client, GEOMETRY_TILE_PATH, layer='parking_site_geometries')

    assert [(feature['properties']['id'], feature['geometry']['type']) for feature in features] == [
        (1, 'Polygon'),
        (2, 'LineString'),
        (3, 'Polygon'),
    ]
    assert features[0]['properties'] == {
        'id': 1,
        'name': 'Demo Parking Site',
        'purpose': 'CAR',
        'type': 'CAR_PARK',
        'capacity': 100,
    }

    # The polygon reaching into the tile from outside is clipped to the tile plus buffer
    for x, y in features[2]['geometry']['coordinates'][0]:
        assert -64 <= x <= 4096 + 64
        assert -64 <= y <= 4096 + 64

    # The point layer still contains just the parking sites with their point in the tile, flagging the ones with a shape
    point_features = get_features(public_api_test_client, GEOMETRY_TILE_PATH)
    assert [
        (feature['properties']['id'], feature['properties'].get('has_geometry', False)) for feature in point_features
    ] == [(1, True), (2, True), (4, False), (5, False)]


def test_get_tile_geometries_filtered(public_api_test_client: FlaskClient, parking_sites_with_geometries: None) -> None:
    features = get_features(
        public_api_test_client, f'{GEOMETRY_TILE_PATH}?purpose=BIKE', layer='parking_site_geometries'
    )

    assert features == []


def test_get_tile_geometries_zoomed_out(
    public_api_test_client: FlaskClient, parking_sites_with_geometries: None
) -> None:
    tile = mercantile.tile(10.0, 50.0, 11)
    path = f'/api/public/v3/tiles/{tile.z}/{tile.x}/{tile.y}.mvt'

    assert get_features(public_api_test_client, path, layer='parking_site_geometries') == []
    point_features = get_features(public_api_test_client, path)
    assert len(point_features) == 5
    # Without shapes in the tile, no point is flagged
    assert not any('has_geometry' in feature['properties'] for feature in point_features)


@pytest.fixture
def on_street_parking_sites(db: SQLAlchemy) -> None:
    source = get_source()
    car_park = get_parking_site(source=source, original_uid='car-park')
    on_street = get_parking_site(
        source=source,
        original_uid='on-street',
        type=ParkingSiteType.ON_STREET,
        lat=Decimal('50.0001'),
        lon=Decimal('10.0001'),
    )
    on_street.geojson = {'type': 'LineString', 'coordinates': [[10.0001, 50.0001], [10.0002, 50.0001]]}
    without_type = get_parking_site(
        source=source,
        original_uid='without-type',
        type=None,
        lat=Decimal('50.0002'),
        lon=Decimal('10.0002'),
    )
    db.session.add_all([car_park, on_street, without_type])
    db.session.commit()


def get_feature_types(
    public_api_test_client: FlaskClient, z: int, query: str = '', layer: str = 'parking_sites'
) -> list:
    tile = mercantile.tile(10.0, 50.0, z)
    features = get_features(
        public_api_test_client, f'/api/public/v3/tiles/{tile.z}/{tile.x}/{tile.y}.mvt{query}', layer
    )
    return sorted(feature['properties'].get('type') or '' for feature in features)


@pytest.mark.parametrize('z', [8, 12])
def test_get_tile_hide_on_street_zoomed_out(
    public_api_test_client: FlaskClient, on_street_parking_sites: None, z: int
) -> None:
    query = '?hide_on_street_until_zoom=12'

    assert get_feature_types(public_api_test_client, z, query) == ['', 'CAR_PARK']
    assert get_feature_types(public_api_test_client, z, query, layer='parking_site_geometries') == []


def test_get_tile_hide_on_street_zoomed_in(public_api_test_client: FlaskClient, on_street_parking_sites: None) -> None:
    query = '?hide_on_street_until_zoom=12'

    assert get_feature_types(public_api_test_client, 13, query) == ['', 'CAR_PARK', 'ON_STREET']
    assert get_feature_types(public_api_test_client, 13, query, layer='parking_site_geometries') == ['ON_STREET']


def test_get_tile_without_hide_on_street(public_api_test_client: FlaskClient, on_street_parking_sites: None) -> None:
    assert get_feature_types(public_api_test_client, 12) == ['', 'CAR_PARK', 'ON_STREET']
