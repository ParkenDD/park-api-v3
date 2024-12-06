"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
import pytest
from flask.testing import FlaskClient

from webapp.models import ParkingSite, Source


@pytest.fixture(scope='function')
def source(db_noreset) -> Source:
    source = Source()



@pytest.fixture(scope='function')
def parking_site(db_noreset) -> ParkingSite:
    parking_site = ParkingSite()
    parking_site.from_dict(
        {
            'source_id': 1,
            'original_uid': 'herrenbergaischbachstrasse',
            'name': 'Aischbachstraße',
            'operator_name': 'Stadt Herrenberg',
            'public_url': 'https://www.herrenberg.de/de/Stadtleben/Erlebnis-Herrenberg/Service/Parkplaetze/Parkplatz?view=publish&item=parkingLocation&id=1016',
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
        }
    )
    db_noreset.session.add(parking_site)
    db_noreset.session.commit()
    print('=' * 50)
    print(db_noreset.session.query(ParkingSite).all())
    print('=' * 50)
    yield parking_site

    # empty_tables(db_noreset, models=[ParkingSite])


def test_get_data(test_client: FlaskClient, parking_site):
    """
    0 - Get the tests to run at all
    1 - Get client to send requests
    2 - Send request
    3 - Read and assert result
    """
    response = test_client.get(
        path='/api/public/v3/parking-sites/1',
    )
    assert response.status_code == 200
