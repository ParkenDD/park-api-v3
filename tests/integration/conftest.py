"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text

from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp import launch
from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.extensions import db as flask_sqlalchemy
from webapp.models import BaseModel, ParkingSite, Source


@pytest.fixture
def db(flask_app: App) -> SQLAlchemy:
    """
    Yields the database as a session-scoped fixture without resetting any content.

    If you use this in a test, make sure to manually reset the affected tables
    at the beginning and end of the test, e.g. by calling empty_tables().
    """
    with flask_app.app_context():
        yield flask_sqlalchemy


def empty_tables(empty_tables: SQLAlchemy, models: list[type[BaseModel]]) -> None:
    """
    Can be used to empty only the tables that are affected by a specific test
    """
    empty_tables.session.close()
    table_names = [model.__tablename__ for model in models]
    with empty_tables.engine.connect() as conn:
        conn.execute(text(f'TRUNCATE {", ".join(table_names)} RESTART IDENTITY CASCADE;'))
        conn.commit()


@pytest.fixture(scope='session')
def flask_app(tmp_path_factory) -> App:
    """
    Creates a Flask app instance configured for testing.
    """

    # Load default development config instead of config.yaml for testing to avoid issues with local setups
    os.environ['CONFIG_FILE'] = 'config_dist_dev.yaml'

    app = launch(testing=True)

    with app.app_context():
        flask_sqlalchemy.drop_all()
        flask_sqlalchemy.create_all()
        yield app


@pytest.fixture(scope='function')
def test_client(flask_app: Flask) -> FlaskClient:
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def multi_source_parking_site_test_data(db: SQLAlchemy) -> None:
    source_1 = get_source(1)
    source_2 = get_source(2)
    source_3 = get_source(3)
    db.session.add(source_1)
    db.session.add(source_2)
    db.session.add(source_3)
    db.session.commit()

    db.session.add(get_parking_site(counter=1, source_id=1))
    db.session.add(get_parking_site(counter=2, source_id=1))
    db.session.add(get_parking_site(counter=3, source_id=1))
    db.session.add(get_parking_site(counter=4, source_id=2))
    db.session.add(get_parking_site(counter=5, source_id=2))
    db.session.add(get_parking_site(counter=6, source_id=3))
    db.session.commit()

    yield

    empty_tables(db, models=[Source, ParkingSite])
