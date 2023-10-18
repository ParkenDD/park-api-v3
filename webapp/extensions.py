"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_migrate import Migrate
from flask_openapi import FlaskOpenapi

from webapp.common.sqlalchemy import SQLAlchemy

from .common.celery import LogErrorsCelery

celery = LogErrorsCelery()
db = SQLAlchemy()
migrate = Migrate()
openapi = FlaskOpenapi()
