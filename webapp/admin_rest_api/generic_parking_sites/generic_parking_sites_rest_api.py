"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
from flask_openapi.decorator import EmptyResponse, ErrorResponse, Request, document
from flask_openapi.schema import JsonSchema, ObjectField

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.admin_rest_api.generic_parking_sites.generic_parking_sites_handler import (
    GenericParkingSitesHandler,
)
from webapp.common.json import empty_json_response
from webapp.dependencies import dependencies


class GenericParkingSitesBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    generic_parking_sites_handler: GenericParkingSitesHandler

    def __init__(self):
        super().__init__('generic-parking-sites', __name__, url_prefix='/generic-parking-sites')

        self.generic_parking_sites_handler = GenericParkingSitesHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '/json',
            view_func=GenericParkingSitesJsonMethodView.as_view(
                'generic-parking-sites-json',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/xml',
            view_func=GenericParkingSitesXmlMethodView.as_view(
                'generic-parking-sites-xml',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/csv',
            view_func=GenericParkingSitesCsvMethodView.as_view(
                'generic-parking-sites-csv',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/xlsx',
            view_func=GenericParkingSitesXlsxMethodView.as_view(
                'generic-parking-sites-xlsx',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )


class GenericParkingSitesMethodView(AdminApiBaseMethodView):
    generic_parking_sites_handler: GenericParkingSitesHandler

    def __init__(self, *, generic_parking_sites_handler: GenericParkingSitesHandler, **kwargs):
        super().__init__(**kwargs)
        self.generic_parking_sites_handler = generic_parking_sites_handler


class GenericParkingSitesJsonMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[
            Request(
                schema=JsonSchema(
                    title='Generic JSON data',
                    properties={},
                    description='Any JSON data',
                )
            )
        ],
        response=[EmptyResponse(), ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        self.generic_parking_sites_handler.handle_json_data(
            data=self.request_helper.get_parsed_json(),
        )

        return empty_json_response(), 204


class GenericParkingSitesXmlMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='application/xml')],
        response=[EmptyResponse(), ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        self.generic_parking_sites_handler.handle_json_data(
            data=self.request_helper.get_parsed_json(),
        )

        return empty_json_response(), 204


class GenericParkingSitesCsvMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='text/csv')],
        response=[EmptyResponse(), ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        self.generic_parking_sites_handler.handle_csv_data(
            data=self.request_helper.get_request_body(),
        )

        return empty_json_response(), 204


class GenericParkingSitesXlsxMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')],
        response=[EmptyResponse(), ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        self.generic_parking_sites_handler.handle_xlsx_data(
            data=self.request_helper.get_request_body(),
        )

        return empty_json_response(), 204
