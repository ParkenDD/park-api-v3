"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from http import HTTPStatus

from flask import jsonify
from flask_openapi.decorator import EmptyResponse, ErrorResponse, Response, ResponseData, SchemaReference, document
from parkapi_sources.models import CombinedParkingSiteInput
from validataclass.validators import DataclassValidator

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.common.json import empty_json_response
from webapp.common.server_auth import ServerAuthHelper
from webapp.dependencies import dependencies
from webapp.shared.parking_restriction.parking_restriction_schema import parking_restriction_component
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput
from webapp.shared.parking_site.parking_sites_schema import parking_site_component
from webapp.shared.parking_site_group.parking_sites_group_schema import parking_site_group_component
from webapp.shared.sources.source_schema import source_component

from .parking_site_handler import ParkingSiteHandler
from .parking_site_schema import (
    apply_parking_site_duplicates_request,
    generate_parking_site_duplicates_request,
    generate_parking_site_duplicates_response,
    parking_site_item_request,
    parking_site_list_request,
    parking_site_list_response,
)
from .parking_site_validators import ApplyDuplicatesInput, GetDuplicatesInput, ParkingSiteListInput


class ParkingSitesBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    parking_site_handler: ParkingSiteHandler

    def __init__(self):
        super().__init__('admin-parking-sites', __name__, url_prefix='/parking-sites')

        self.parking_site_handler = ParkingSiteHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            matching_service=dependencies.get_matching_service(),
            source_repository=dependencies.get_source_repository(),
            generic_parking_site_import_service=dependencies.get_generic_parking_site_import_service(),
        )

        self.add_url_rule(
            '',
            view_func=ParkingSitesMethodView.as_view(
                'admin-parking-sites',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/upsert-list',
            view_func=ParkingSiteUpsertListMethodView.as_view(
                'admin-upsert-parking-site-list',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/upsert-item',
            view_func=ParkingSiteUpsertItemMethodView.as_view(
                'admin-upsert-parking-site-item',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/<int:parking_site_id>',
            view_func=ParkingSiteMethodView.as_view(
                'admin-parking-site',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/duplicates/generate',
            view_func=ParkingSiteDuplicatesGenerateMethodView.as_view(
                'admin-parking-site-duplicates-generate',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/duplicates/apply',
            view_func=ParkingSiteDuplicatesApplyMethodView.as_view(
                'admin-parking-site-duplicates-apply',
                **self.get_base_method_view_dependencies(),
                server_auth_helper=dependencies.get_server_auth_helper(),
                parking_site_handler=self.parking_site_handler,
            ),
        )


class ParkingSiteBaseMethodView(AdminApiBaseMethodView):
    parking_site_handler: ParkingSiteHandler

    def __init__(self, *, parking_site_handler: ParkingSiteHandler, server_auth_helper: ServerAuthHelper, **kwargs):
        super().__init__(**kwargs)
        self.parking_site_handler = parking_site_handler
        self.server_auth_helper = server_auth_helper


class ParkingSitesMethodView(ParkingSiteBaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    def get(self):
        search_query = self.validate_query_args(self.parking_site_search_query_validator)

        parking_sites = self.parking_site_handler.get_parking_sites(search_query=search_query)

        return self.jsonify_paginated_response(
            parking_sites,
            search_query=search_query,
        ), HTTPStatus.OK


class ParkingSiteMethodView(ParkingSiteBaseMethodView):
    def get(self, parking_site_id: int):
        self.parking_site_handler.get_parking_site(parking_site_id)


class ParkingSiteUpsertListMethodView(ParkingSiteBaseMethodView):
    parking_site_list_validator = DataclassValidator(ParkingSiteListInput)

    @document(
        request=parking_site_list_request,
        response=[
            parking_site_list_response,
            ErrorResponse(
                error_codes=[
                    HTTPStatus.BAD_REQUEST,
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.NOT_FOUND,
                ],
            ),
        ],
        components=[
            source_component,
            parking_site_component,
            parking_restriction_component,
            parking_site_group_component,
        ],
    )
    def post(self):
        list_input: ParkingSiteListInput = self.validate_request(self.parking_site_list_validator)

        response = self.parking_site_handler.upsert_parking_site_list(
            source_uid=self.server_auth_helper.get_current_user().username,
            parking_site_dicts=list_input.items,
        )

        return jsonify(response), HTTPStatus.OK


class ParkingSiteUpsertItemMethodView(ParkingSiteBaseMethodView):
    combined_parking_site_validator = DataclassValidator(CombinedParkingSiteInput)

    @document(
        request=parking_site_item_request,
        response=[
            Response(ResponseData(SchemaReference('ParkingSite'))),
            ErrorResponse(
                error_codes=[
                    HTTPStatus.BAD_REQUEST,
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.NOT_FOUND,
                ],
            ),
        ],
        components=[
            source_component,
            parking_site_component,
            parking_restriction_component,
            parking_site_group_component,
        ],
    )
    def post(self):
        parking_site: CombinedParkingSiteInput = self.validate_request(self.combined_parking_site_validator)

        response = self.parking_site_handler.upsert_parking_site_item(
            source_uid=self.server_auth_helper.get_current_user().username,
            combined_parking_site_input=parking_site,
        )

        return jsonify(response), HTTPStatus.OK


class ParkingSiteDuplicatesGenerateMethodView(ParkingSiteBaseMethodView):
    duplicate_validator = DataclassValidator(GetDuplicatesInput)

    @document(
        description='Generate ParkingSite duplicates.',
        request=generate_parking_site_duplicates_request,
        response=[generate_parking_site_duplicates_response, ErrorResponse(error_codes=[400, 401])],
    )
    def post(self):
        duplicate_input: GetDuplicatesInput = self.duplicate_validator.validate(self.request_helper.get_parsed_json())

        duplicate_items = self.parking_site_handler.generate_duplicates(duplicate_input)

        return {'items': duplicate_items, 'total_count': len(duplicate_items)}, HTTPStatus.OK


class ParkingSiteDuplicatesApplyMethodView(ParkingSiteBaseMethodView):
    apply_duplicate_validator = DataclassValidator(ApplyDuplicatesInput)

    @document(
        description='Apply ParkingSite duplicates.',
        request=apply_parking_site_duplicates_request,
        response=[EmptyResponse(), ErrorResponse(error_codes=[400, 401])],
    )
    def post(self):
        apply_duplicate_input: ApplyDuplicatesInput = self.validate_request(self.apply_duplicate_validator)

        self.parking_site_handler.apply_duplicates(apply_duplicate_input)

        return empty_json_response(), HTTPStatus.NO_CONTENT
