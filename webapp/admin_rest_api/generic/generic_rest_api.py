"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Response, jsonify
from flask_openapi.decorator import ErrorResponse, Request, document
from flask_openapi.schema import JsonSchema
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.dependencies import dependencies

from .generic_handler import GenericHandler
from .generic_schema import generic_parking_site_response


class GenericBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    generic_parking_sites_handler: GenericHandler

    def __init__(self):
        super().__init__('generic', __name__, url_prefix='/generic')

        self.request_helper = dependencies.get_request_helper()
        self.config_helper = dependencies.get_config_helper()

        self.generic_parking_sites_handler = GenericHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            parking_site_history_repository=dependencies.get_parking_site_history_repository(),
            parking_spot_repository=dependencies.get_parking_spot_repository(),
            source_repository=dependencies.get_source_repository(),
            generic_import_service=dependencies.get_generic_import_service(),
        )

        self.add_url_rule(
            '/json',
            view_func=GenericJsonMethodView.as_view(
                'generic-json',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/xml',
            view_func=GenericXmlMethodView.as_view(
                'generic-xml',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/csv',
            view_func=GenericCsvMethodView.as_view(
                'generic-csv',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )
        self.add_url_rule(
            '/xlsx',
            view_func=GenericXlsxMethodView.as_view(
                'generic-xlsx',
                **self.get_base_method_view_dependencies(),
                generic_parking_sites_handler=self.generic_parking_sites_handler,
            ),
        )

        @self.after_request
        def after_request(response: Response):
            source_uid = self.request_helper.get_basicauth_username()

            if source_uid is None or source_uid not in self.config_helper.get('DEBUG_SOURCES', []):
                return response

            debug_dump_dir = Path(self.config_helper.get('DEBUG_DUMP_DIR'), source_uid)
            os.makedirs(debug_dump_dir, exist_ok=True)

            metadata_file_path = Path(debug_dump_dir, f'{datetime.now(timezone.utc).isoformat()}-metadata')
            request_body_file_path = Path(debug_dump_dir, f'{datetime.now(timezone.utc).isoformat()}-request-body')

            metadata = [
                f'URL: {self.request_helper.get_path()}',
                f'Method: {self.request_helper.get_method()}',
                f'HTTP Status: {response.status_code}',
                '',
                'Request Headers:',
                *[f'{key}: {value}' for key, value in self.request_helper.get_headers().items()],
                '',
                'Response Headers:',
                *[f'{key}: {value}' for key, value in response.headers.items()],
                '',
                'Response Body:',
            ]
            if response.data:
                metadata.append(response.get_data(as_text=True))

            with metadata_file_path.open('w') as metadata_file:
                metadata_file.writelines('\n'.join(metadata))

            with request_body_file_path.open('wb') as request_file:
                request_file.write(self.request_helper.get_request_body())

            return response


class GenericMethodView(AdminApiBaseMethodView):
    generic_parking_sites_handler: GenericHandler

    def __init__(self, *, generic_parking_sites_handler: GenericHandler, **kwargs):
        super().__init__(**kwargs)
        self.generic_parking_sites_handler = generic_parking_sites_handler

    @staticmethod
    def _generate_response(
        parking_inputs: list[
            StaticParkingSiteInput | RealtimeParkingSiteInput | StaticParkingSpotInput | RealtimeParkingSpotInput
        ],
        parking_errors: list[ImportParkingSiteException | ImportParkingSpotException],
    ) -> dict:
        static_parking_site_inputs = [item for item in parking_inputs if isinstance(item, StaticParkingSiteInput)]
        realtime_parking_site_inputs = [item for item in parking_inputs if isinstance(item, RealtimeParkingSiteInput)]
        static_parking_spot_inputs = [item for item in parking_inputs if isinstance(item, StaticParkingSpotInput)]
        realtime_parking_spot_inputs = [item for item in parking_inputs if isinstance(item, RealtimeParkingSpotInput)]

        parking_site_errors = [
            parking_error for parking_error in parking_errors if isinstance(parking_error, ImportParkingSiteException)
        ]
        parking_spot_errors = [
            parking_error for parking_error in parking_errors if isinstance(parking_error, ImportParkingSpotException)
        ]

        return {
            'parking_sites': {
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
            },
            'parking_spots': {
                'summary': {
                    'static_success_count': len(static_parking_spot_inputs),
                    'realtime_success_count': len(realtime_parking_spot_inputs),
                    'error_count': len(parking_errors),
                },
                'errors': [
                    {
                        'message': error.message,
                        'parking_spot_errors': error.parking_spot_uid,
                        'source_uid': error.source_uid,
                    }
                    for error in parking_spot_errors
                ],
            },
        }


class GenericJsonMethodView(GenericMethodView):
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


class GenericXmlMethodView(GenericMethodView):
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


class GenericCsvMethodView(GenericMethodView):
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


class GenericXlsxMethodView(GenericMethodView):
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
