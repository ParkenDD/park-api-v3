"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from flask import jsonify
from flask_openapi.decorator import (
    ErrorResponse,
    Parameter,
    Response,
    ResponseData,
    document,
)
from flask_openapi.schema import StringField
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.public_rest_api.park_api_v1.park_api_v1_handler import ParkApiV1Handler
from webapp.public_rest_api.park_api_v1.park_api_v1_schema import (
    park_api_v1_parking_site_example,
    park_api_v1_parking_site_schema,
    park_api_v1_sources_example,
    park_api_v1_sources_schema,
)
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkApiV1Blueprint(PublicApiBaseBlueprint):
    documented: bool = True
    park_api_v1_handler: ParkApiV1Handler

    def __init__(self):
        super().__init__('park-api-v1', __name__, url_prefix='/v1')

        self.park_api_v1_handler = ParkApiV1Handler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '',
            view_func=ParkApiV1SourceMethodView.as_view(
                'parking-source',
                **self.get_base_method_view_dependencies(),
                park_api_v1_handler=self.park_api_v1_handler,
            ),
        )

        self.add_url_rule(
            '/<source_uid>',
            view_func=ParkApiV1ParkingSiteMethodView.as_view(
                'parking-sites-by-source',
                **self.get_base_method_view_dependencies(),
                park_api_v1_handler=self.park_api_v1_handler,
            ),
        )


class ParkApiV1BaseMethodView(PublicApiBaseMethodView):
    park_api_v1_handler: ParkApiV1Handler

    def __init__(self, *, park_api_v1_handler: ParkApiV1Handler, **kwargs):
        super().__init__(**kwargs)
        self.park_api_v1_handler = park_api_v1_handler


class ParkApiV1SourceMethodView(ParkApiV1BaseMethodView):
    @document(
        description='Get ParkApi V1 Sources.',
        response=[Response(ResponseData(park_api_v1_sources_schema, park_api_v1_sources_example))],
    )
    def get(self):
        result = self.park_api_v1_handler.get_sources_as_dict()

        return jsonify(result)


class ParkApiV1ParkingSiteMethodView(ParkApiV1BaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    @document(
        description='Get ParkApi V1 Parking Sites.',
        path=[
            Parameter(
                'source_uid',
                schema=StringField(minLength=1, maxLength=256, example='example-city'),
            )
        ],
        response=[Response(ResponseData(park_api_v1_parking_site_schema, park_api_v1_parking_site_example))],
    )
    def get(self, source_uid: str):
        search_query = self.parking_site_search_query_validator.validate(
            {
                **self.request_helper.get_query_args(),
                'source_uid': source_uid,
            },
        )

        result = self.park_api_v1_handler.get_parking_site_list_as_dict(search_query)

        return jsonify(result)
