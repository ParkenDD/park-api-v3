"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from http import HTTPStatus

from flask import jsonify
from flask_openapi.decorator import ErrorResponse, ExampleReference, Response, ResponseData, SchemaReference, document
from validataclass.validators import DataclassValidator

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.common.server_auth import ServerAuthHelper
from webapp.dependencies import dependencies
from webapp.shared.sources.source_schema import source_component

from .source_handler import SourceHandler
from .source_schemas import source_request
from .source_validators import SourceInput


class SourceBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    source_handler: SourceHandler

    def __init__(self):
        super().__init__('admin-sources', __name__, url_prefix='/sources')

        self.source_handler = SourceHandler(
            **self.get_base_handler_dependencies(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '',
            view_func=SourcesMethodView.as_view(
                'admin-sources',
                **self.get_base_method_view_dependencies(),
                source_handler=self.source_handler,
                server_auth_helper=dependencies.get_server_auth_helper(),
            ),
        )


class SourceBaseMethodView(AdminApiBaseMethodView):
    source_handler: SourceHandler
    server_auth_helper: ServerAuthHelper

    def __init__(self, *, source_handler: SourceHandler, server_auth_helper: ServerAuthHelper, **kwargs):
        super().__init__(**kwargs)
        self.source_handler = source_handler
        self.server_auth_helper = server_auth_helper


class SourcesMethodView(SourceBaseMethodView):
    source_validator = DataclassValidator(SourceInput)

    @document(
        request=source_request,
        response=[
            Response(
                ResponseData(SchemaReference('Source'), ExampleReference('Source')),
                http_status=HTTPStatus.OK,
            ),
            Response(
                ResponseData(SchemaReference('Source'), ExampleReference('Source')),
                http_status=HTTPStatus.CREATED,
            ),
            ErrorResponse(
                error_codes=[
                    HTTPStatus.BAD_REQUEST,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.NO_CONTENT,
                ],
            ),
        ],
        components=[source_component],
    )
    def post(self):
        source_input = self.validate_request(
            self.source_validator,
            context_args={'source_uid': self.server_auth_helper.get_current_user().username},
        )

        source, created = self.source_handler.upsert_source(source_input=source_input)

        return jsonify(source), HTTPStatus.CREATED if created else HTTPStatus.OK
