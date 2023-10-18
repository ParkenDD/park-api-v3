"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import current_app, request

from webapp.common.blueprint import Blueprint
from webapp.dependencies import dependencies


class AdminApiBaseBlueprint(Blueprint):
    auth_required = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.auth_required:

            @self.before_request
            def before_request():
                if getattr(
                    current_app.view_functions[request.endpoint],
                    'skip_basic_auth',
                    False,
                ):
                    return
                # Authenticate user via Basic Auth (raises AdminApiUnauthorizedException if unauthenticated)
                server_auth_helper = dependencies.get_server_auth_helper()
                server_auth_helper.authenticate_request(request)

    @staticmethod
    def get_base_handler_dependencies() -> dict:
        return {
            'logger': dependencies.get_logger(),
            'config_helper': dependencies.get_config_helper(),
            'event_helper': dependencies.get_event_helper(),
        }

    @staticmethod
    def get_base_method_view_dependencies() -> dict:
        return {
            'logger': dependencies.get_logger(),
            'request_helper': dependencies.get_request_helper(),
            'config_helper': dependencies.get_config_helper(),
        }
