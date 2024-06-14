"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os


class BaseConfig:
    INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')  # noqa: S108

    PROJECT_NAME = 'park-api'
    PROJECT_VERSION = '0.9'

    DEBUG = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    LOG_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, 'logs'))
    TEMP_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, 'temp'))

    REDIS_URL = 'redis://redis:6379/3'
    ENFORCE_CONFIG_VALUES = ['SQLALCHEMY_DATABASE_URI', 'CELERY_BROKER_URL']

    REMOTE_SERVERS: dict = {}
    SERVER_AUTH_USERS: dict = {}

    PARK_API_CONVERTER: []

    OPENAPI_LOGIN_REQUIRED = False

    # This will be the title of the generated html sites:
    DOCUMENTATION_TITLE = 'ParkAPI Documentation'

    # Default title for all APIs of your project:
    OPENAPI_TITLE = 'ParkAPI Service'

    # Default description for all APIs of your project:
    OPENAPI_DESCRIPTION = 'This is the OpenAPI documentation for the ParkAPI service.'

    # E-mail address where users of the project's APIs can contact you:
    OPENAPI_CONTACT_MAIL = 'mail@binary-butterfly.de'

    # URL of a 'Terms of Service' document applicable for your project:
    OPENAPI_TOS = 'https://binary-butterfly.de'

    # A list of all servers that the documented project runs on.
    # (An additional 'development' entry for this list will be generated automatically
    # if you're running it locally for development.)
    OPENAPI_SERVERS = [
        {'url': 'https://binary-butterfly.de', 'description': 'prod'},
    ]

    # Switch parking site metrics to True for metrics on parking site level. Keep in mind that this adds a lot of data to your metrics
    # endpoint, so the systems using these metrics should have enough power and proper administration.
    PARKING_SITE_METRICS = False

    # set
    STATIC_GEOJSON_BASE_URL = 'https://raw.githubusercontent.com/ParkenDD/parkapi-sources-v3/main/data/'
