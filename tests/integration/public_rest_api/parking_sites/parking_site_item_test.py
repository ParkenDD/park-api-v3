"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import ANY

import pytest
from flask.testing import FlaskClient

from tests.integration.conftest import empty_tables
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.models import ParkingSite, Source


@pytest.fixture(scope='function')
def source(db: SQLAlchemy) -> Source:
    source = Source(
        uid='0' * 10,
        name='Test Source',
        static_parking_site_error_count=0,
        realtime_parking_site_error_count=0,
    )
    return source


@pytest.fixture(scope='function')
def parking_site(source: Source) -> ParkingSite:
    parking_site = ParkingSite()
    parking_site.from_dict({
        'original_uid': 'herrenbergaischbachstrasse',
        'name': 'Aischbachstraße',
        'operator_name': 'Stadt Herrenberg',
        'public_url': 'https://www.herrenberg.de/de/Stadtleben/Erlebnis-Herrenberg/Service/Parkplaetze/Parkplatz?'
        'view=publish&item=parkingLocation&id=1016',
        'address': '71083 Herrenberg',
        'description': 'Parken mit Parkscheibe',
        'type': 'OFF_STREET_PARKING_GROUND',
        'purpose': 'CAR',
        'has_fee': False,
        'has_realtime_data': False,
        'lat': '48.5963190',
        'lon': '8.8654610',
        'capacity': 58,
        'opening_hours': 'Mo - Su 08:00-17:00',
    })
    parking_site.source = source
    return parking_site


@pytest.fixture(scope='function')
def fill_database(db: SQLAlchemy, parking_site: ParkingSite) -> ParkingSite:
    db.session.add(parking_site)
    db.session.commit()

    yield

    empty_tables(db, models=[Source, ParkingSite])


def test_get_data(test_client: FlaskClient, fill_database: None):
    """
    Check that we get correctly one parking site from the endpoint.
    """
    response = test_client.get(
        path='/api/public/v3/parking-sites/1',
    )
    assert response.status_code == 200
    assert response.json == {
        'source_id': 1,
        'original_uid': 'herrenbergaischbachstrasse',
        'name': 'Aischbachstraße',
        'operator_name': 'Stadt Herrenberg',
        'public_url': 'https://www.herrenberg.de/de/Stadtleben/Erlebnis-Herrenberg/Service/Parkplaetze/Parkplatz?'
        'view=publish&item=parkingLocation&id=1016',
        'address': '71083 Herrenberg',
        'description': 'Parken mit Parkscheibe',
        'type': 'OFF_STREET_PARKING_GROUND',
        'purpose': 'CAR',
        'has_fee': False,
        'has_realtime_data': False,
        'lat': '48.5963190',
        'lon': '8.8654610',
        'capacity': 58,
        'opening_hours': 'Mo - Su 08:00-17:00',
        'id': 1,
        'created_at': ANY,
        'modified_at': ANY,
    }
