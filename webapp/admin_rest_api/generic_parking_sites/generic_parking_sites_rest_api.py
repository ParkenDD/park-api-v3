"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import ErrorResponse, Request, document
from flask_openapi.schema import JsonSchema
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.admin_rest_api.generic_parking_sites.generic_parking_site_schema import generic_parking_site_response
from webapp.admin_rest_api.generic_parking_sites.generic_parking_sites_handler import GenericParkingSitesHandler
from webapp.dependencies import dependencies


class GenericParkingSitesBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    generic_parking_sites_handler: GenericParkingSitesHandler

    def __init__(self):
        super().__init__('generic-parking-sites', __name__, url_prefix='/generic-parking-sites')

        self.generic_parking_sites_handler = GenericParkingSitesHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            parking_site_history_repository=dependencies.get_parking_site_history_repository(),
            source_repository=dependencies.get_source_repository(),
            parking_site_generic_import_service=dependencies.get_parking_site_generic_import_service(),
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

    @staticmethod
    def _generate_response(
        parking_site_inputs: list[StaticParkingSiteInput | RealtimeParkingSiteInput],
        parking_site_errors: list[ImportParkingSiteException],
    ) -> dict:
        static_parking_site_inputs = [item for item in parking_site_inputs if isinstance(item, StaticParkingSiteInput)]
        realtime_parking_site_inputs = [item for item in parking_site_inputs if isinstance(item, RealtimeParkingSiteInput)]

        return {
            'summary': {
                'static_success_count': len(static_parking_site_inputs),
                'realtime_success_count': len(realtime_parking_site_inputs),
                'error_count': len(parking_site_errors),
            },
            'errors': [
                {
                    'message': error.message,
                    'parking_site_uid': error.parking_site_uid,
                    'source_uid': error.source_uid,
                }
                for error in parking_site_errors
            ],
        }


class GenericParkingSitesJsonMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[
            Request(
                schema=JsonSchema(
                    title='Generic JSON data',
                    properties={},
                    description='Any JSON data',
                ),
            ),
        ],
        response=[generic_parking_site_response, ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        parking_site_inputs, parking_site_errors = self.generic_parking_sites_handler.handle_json_data(
            source_uid=self.request_helper.get_basicauth_username(),
            data=self.request_helper.get_parsed_json(),
        )

        return jsonify(self._generate_response(parking_site_inputs, parking_site_errors))


class GenericParkingSitesXmlMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='application/xml')],
        response=[generic_parking_site_response, ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        parking_site_inputs, parking_site_errors = self.generic_parking_sites_handler.handle_xml_data(
            source_uid=self.request_helper.get_basicauth_username(),
            data=self.request_helper.get_request_body(),
        )

        return jsonify(self._generate_response(parking_site_inputs, parking_site_errors))


class GenericParkingSitesCsvMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='text/csv')],
        response=[generic_parking_site_response, ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        parking_site_inputs, parking_site_errors = self.generic_parking_sites_handler.handle_csv_data(
            source_uid=self.request_helper.get_basicauth_username(),
            data=self.request_helper.get_request_body_text(),
        )

        return jsonify(self._generate_response(parking_site_inputs, parking_site_errors))


class GenericParkingSitesXlsxMethodView(GenericParkingSitesMethodView):
    @document(
        description='POST update.',
        request=[Request(mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')],
        response=[generic_parking_site_response, ErrorResponse(error_codes=[400, 403])],
    )
    def post(self):
        parking_site_inputs, parking_site_errors = self.generic_parking_sites_handler.handle_xlsx_data(
            source_uid=self.request_helper.get_basicauth_username(),
            data=self.request_helper.get_request_body(),
        )

        return jsonify(self._generate_response(parking_site_inputs, parking_site_errors))
