"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from http import HTTPStatus

from flask import jsonify
from flask_openapi.decorator import ErrorResponse, ExampleReference, Response, ResponseData, SchemaReference, document
from parkapi_sources.models import CombinedParkingSpotInput
from validataclass.validators import DataclassValidator

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.common.server_auth import ServerAuthHelper
from webapp.dependencies import dependencies
from webapp.shared.parking_restriction.parking_restriction_schema import parking_restriction_component
from webapp.shared.parking_spot.parking_spot_schema import parking_spot_component

from .parking_spot_handler import ParkingSpotHandler
from .parking_spot_schema import parking_spot_request


class ParkingSpotBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    parking_spot_handler: ParkingSpotHandler

    def __init__(self):
        super().__init__('admin-parking-spots', __name__, url_prefix='/parking-spots')

        self.parking_spot_handler = ParkingSpotHandler(
            **self.get_base_handler_dependencies(),
            source_repository=dependencies.get_source_repository(),
            generic_parking_spot_import_service=dependencies.get_generic_parking_spot_import_service(),
        )

        self.add_url_rule(
            '',
            view_func=ParkingSpotsMethodView.as_view(
                'admin-parking-spots',
                **self.get_base_method_view_dependencies(),
                parking_spot_handler=self.parking_spot_handler,
                server_auth_helper=dependencies.get_server_auth_helper(),
            ),
        )


class ParkingSpotBaseMethodView(AdminApiBaseMethodView):
    parking_spot_handler: ParkingSpotHandler
    server_auth_helper: ServerAuthHelper

    def __init__(self, *, parking_spot_handler: ParkingSpotHandler, server_auth_helper: ServerAuthHelper, **kwargs):
        super().__init__(**kwargs)
        self.parking_spot_handler = parking_spot_handler
        self.server_auth_helper = server_auth_helper


class ParkingSpotsMethodView(ParkingSpotBaseMethodView):
    combined_parking_spot_validator = DataclassValidator(CombinedParkingSpotInput)

    @document(
        request=parking_spot_request,
        response=[
            Response(
                ResponseData(
                    schema=SchemaReference('ParkingSpot'),
                    example=ExampleReference('ParkingSpot'),
                ),
                http_status=HTTPStatus.OK,
            ),
            Response(
                ResponseData(
                    schema=SchemaReference('ParkingSpot'),
                    example=ExampleReference('ParkingSpot'),
                ),
                http_status=HTTPStatus.CREATED,
            ),
            ErrorResponse(
                error_codes=[
                    HTTPStatus.BAD_REQUEST,
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.NOT_FOUND,
                ],
            ),
        ],
        components=[parking_spot_component, parking_restriction_component],
    )
    def post(self):
        combined_parking_spot_input = self.validate_request(self.combined_parking_spot_validator)

        parking_spot, created = self.parking_spot_handler.upsert_parking_spot(
            source_uid=self.server_auth_helper.get_current_user().username,
            combined_parking_spot_input=combined_parking_spot_input,
        )
        parking_spot_dict = parking_spot.to_dict(include_parking_restrictions=True)

        return jsonify(parking_spot_dict), HTTPStatus.CREATED if created else HTTPStatus.OK
