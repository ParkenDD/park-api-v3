"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
from pathlib import Path

from flask import Flask
from yaml import safe_load

from webapp.common.remote_helper import RemoteServer, RemoteServerType

from .base_config import BaseConfig


class ConfigLoader:
    @staticmethod
    def configure_app(app: Flask, testing: bool = False) -> None:
        """
        Initializes the app config with default values and loads the actual config from a YAML file.
        """
        # Load base config (containing constants and default values)
        app.config.from_object(BaseConfig)

        # load all PARK_API-prefixed values from prefixed ENV
        app.config.from_prefixed_env('PARK_API')

        # load postgresql credentials from env
        if (
            os.getenv('PARK_API_POSTGRES_USER')
            and os.getenv('PARK_API_POSTGRES_DB')
            and os.getenv('PARK_API_POSTGRES_PASSWORD')
            and os.getenv('PARK_API_POSTGRES_HOST')
        ):
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                f'postgresql://{os.getenv("PARK_API_POSTGRES_USER")}:{os.getenv("PARK_API_POSTGRES_PASSWORD")}'
                f'@{os.getenv("PARK_API_POSTGRES_HOST")}/{os.getenv("PARK_API_POSTGRES_DB")}'
            )

        # Load config from yaml file
        config_path = Path(app.config['PROJECT_ROOT']).parent.joinpath(os.getenv('CONFIG_FILE', 'config.yaml'))
        app.config.from_file(config_path, safe_load)

        # load additional secrets config from yaml file (if it exists)
        config_secrets_path = Path(app.config['PROJECT_ROOT']).parent.joinpath(
            os.getenv('CONFIG_SECRETS_FILE', 'config.secrets.yaml'),
        )
        if config_secrets_path.exists():
            app.config.from_file(config_secrets_path, safe_load)

        app.config['MODE'] = os.getenv('APPLICATION_MODE', 'DEVELOPMENT')

        # Transform REMOTE_SERVERS entries into RemoteServer dataclass objects
        app.config['REMOTE_SERVERS'] = {
            RemoteServerType[key]: RemoteServer(
                url=server['url'],
                user=server['user'],
                password=server['password'],
                cert=server.get('cert'),
            )
            for key, server in app.config['REMOTE_SERVERS'].items()
        }

        # Ensure that important config values are set
        config_check = [key for key in app.config['ENFORCE_CONFIG_VALUES'] if key not in app.config]
        if len(config_check) > 0:
            raise Exception(f'missing config values: {", ".join(config_check)}')

        if testing:
            app.config['TESTING'] = True
