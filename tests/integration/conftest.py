"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tests.integration.helpers import OpenApiApp
from tests.model_generator.parking_site import get_parking_site, get_parking_site_by_counter
from tests.model_generator.parking_spot import get_parking_spot, get_parking_spot_by_counter
from tests.model_generator.source import get_source, get_source_by_counter
from webapp import launch
from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.extensions import db as flask_sqlalchemy
from webapp.models import ParkingSite, ParkingSpot


@pytest.fixture
def flask_app() -> Generator[App, None, None]:
    """
    Creates a Flask app instance configured for testing.
    """

    # Load default development config instead of config.yaml for testing to avoid issues with local setups
    os.environ['CONFIG_FILE'] = os.environ.get('TEST_CONFIG_FILE', 'config_dist_dev.yaml')

    app = launch(
        app_class=OpenApiApp,
        config_overrides={
            'TESTING': True,
            'DEBUG': True,
            'SERVER_NAME': 'localhost:5000',
        },
    )

    with app.app_context():
        flask_sqlalchemy.drop_all()
        flask_sqlalchemy.create_all()
        yield app


@pytest.fixture
def db(flask_app: App) -> Generator[SQLAlchemy, None, None]:
    """
    Yields the database as a session-scoped fixture without resetting any content.

    If you use this in a test, make sure to manually reset the affected tables
    at the beginning and end of the test, e.g. by calling empty_tables().
    """
    with flask_app.app_context():
        yield flask_sqlalchemy


@pytest.fixture
def test_client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def inserted_parking_site(db: SQLAlchemy) -> ParkingSite:
    parking_site = get_parking_site(source=get_source())
    db.session.add(parking_site)
    db.session.commit()

    return parking_site


@pytest.fixture
def inserted_parking_spot(db: SQLAlchemy) -> ParkingSpot:
    parking_spot = get_parking_spot(source=get_source())
    db.session.add(parking_spot)
    db.session.commit()

    return parking_spot


@pytest.fixture
def multi_source_parking_site_test_data(db: SQLAlchemy) -> None:
    source_1 = get_source_by_counter(1)
    source_2 = get_source_by_counter(2)
    source_3 = get_source_by_counter(3)

    db.session.add(get_parking_site_by_counter(counter=1, source=source_1))
    db.session.add(get_parking_site_by_counter(counter=2, source=source_1))
    db.session.add(get_parking_site_by_counter(counter=3, source=source_1))
    db.session.add(get_parking_site_by_counter(counter=4, source=source_2))
    db.session.add(get_parking_site_by_counter(counter=5, source=source_2))
    db.session.add(get_parking_site_by_counter(counter=6, source=source_3))

    db.session.commit()


@pytest.fixture
def multi_source_parking_spot_test_data(db: SQLAlchemy) -> None:
    source_1 = get_source_by_counter(1)
    source_2 = get_source_by_counter(2)
    source_3 = get_source_by_counter(3)

    db.session.add(get_parking_spot_by_counter(counter=1, source=source_1))
    db.session.add(get_parking_spot_by_counter(counter=2, source=source_1))
    db.session.add(get_parking_spot_by_counter(counter=3, source=source_1))
    db.session.add(get_parking_spot_by_counter(counter=4, source=source_2))
    db.session.add(get_parking_spot_by_counter(counter=5, source=source_2))
    db.session.add(get_parking_spot_by_counter(counter=6, source=source_3))

    db.session.commit()
