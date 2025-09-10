"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Blueprint as FlaskBlueprint

from webapp.dependencies import dependencies


class Blueprint(FlaskBlueprint):
    documentation_base: bool = False
    documented: bool = False
    documentation_auth: bool = False

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
