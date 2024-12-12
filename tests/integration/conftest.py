"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
import re
from collections import namedtuple

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine, text

from webapp import launch
from webapp.extensions import db as flask_sqlalchemy
from webapp.models import BaseModel


@pytest.fixture(scope='session')
def db_noreset(flask_app: Flask):
    """
    Yields the database as a session-scoped fixture without resetting any content.

    If you use this in a test, make sure to manually reset the affected tables
    at the beginning and end of the test, e.g. by calling empty_tables().
    """
    with flask_app.app_context():
        yield flask_sqlalchemy


def empty_tables(db_noreset, models: list[type[BaseModel]]):
    """
    Can be used to empty only the tables that are affected by a specific test
    """
    db_noreset.session.close()
    table_names = [model.__tablename__ for model in models]
    with db_noreset.engine.connect() as conn:
        conn.execute(text(f'TRUNCATE {", ".join(table_names)} RESTART IDENTITY CASCADE;'))
        conn.commit()


@pytest.fixture(scope='session')
def flask_app(tmp_path_factory) -> Flask:
    """
    Creates a Flask app instance configured for testing.
    """

    # Load default development config instead of config.yaml for testing to avoid issues with local setups
    os.environ['CONFIG_FILE'] = 'config_dist_dev.yaml'

    app = launch(testing=True)

    # Create the database and the database tables
    # db_path should be 'mysql+pymysql://root:root@mysql' if
    # SQLALCHEMY_DATABASE_URI: 'mysql+pymysql://root:root@mysql/backend?charset=utf8mb4' is set in test_config.yaml
    db_path: str = re.sub(r'/[^/]+$', '', app.config.get('SQLALCHEMY_DATABASE_URI'))

    engine = create_engine(db_path)
    # We use DROP + CREATE here because it's faster and more reliable in case of foreign keys
    with engine.connect() as connection:
        connection.execution_options(isolation_level='AUTOCOMMIT')
        query_drop_db = 'DROP DATABASE IF EXISTS park_api;'
        query_create_db = 'CREATE DATABASE park_api;'
        connection.execute(text(query_drop_db))
        connection.execute(text(query_create_db))

    with app.app_context():
        flask_sqlalchemy.create_all()
        yield app


@pytest.fixture(scope='function')
def test_client(flask_app: Flask) -> FlaskClient:
    with flask_app.test_client() as client:
        yield client
