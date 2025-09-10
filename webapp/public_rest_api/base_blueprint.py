"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.blueprint import Blueprint
from webapp.dependencies import dependencies


class PublicApiBaseBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_base_handler_dependencies() -> dict:
        return {
            'config_helper': dependencies.get_config_helper(),
            'event_helper': dependencies.get_event_helper(),
        }

    @staticmethod
    def get_base_method_view_dependencies() -> dict:
        return {
            'request_helper': dependencies.get_request_helper(),
            'config_helper': dependencies.get_config_helper(),
        }
