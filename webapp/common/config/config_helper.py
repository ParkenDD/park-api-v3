"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING, Any, Optional

from flask import Config

if TYPE_CHECKING:
    from webapp.app import App


class ConfigHelper:
    """
    Helper class that wraps the application config.
    """

    app: 'App'

    def __init__(self, app: Optional['App'] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def get_config(self) -> Config:
        return self.app.config

    def get(self, key: str, default: Any = None) -> Any:
        return self.app.config.get(key, default)
