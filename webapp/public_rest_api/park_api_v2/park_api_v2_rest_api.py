"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import Parameter, Response, ResponseData, document
from flask_openapi.schema import ArrayField, DecimalField, IntegerField, StringField
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.public_rest_api.park_api_v2.park_api_v2_handler import ParkApiV2Handler
from webapp.public_rest_api.park_api_v2.park_api_v2_schema import (
    park_api_v2_parking_sites_example,
    park_api_v2_parking_sites_schema,
    park_api_v2_source_example,
    park_api_v2_source_schema,
)
from webapp.shared.parking_site import GenericParkingSiteHandler
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkApiV2Blueprint(PublicApiBaseBlueprint):
    documented: bool = True
    park_api_v2_handler: ParkApiV2Handler

    def __init__(self):
        super().__init__('park-api-v2', __name__, url_prefix='/v2')

        self.park_api_v2_handler = ParkApiV2Handler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '/lots/',
            view_func=ParkApiV2LotsMethodView.as_view(
                'parking-sites',
                **self.get_base_method_view_dependencies(),
                park_api_v2_handler=self.park_api_v2_handler,
            ),
        )

        self.add_url_rule(
            '/pools/<pool_id>/',
            view_func=ParkApiV2PoolsMethodView.as_view(
                'sources',
                **self.get_base_method_view_dependencies(),
                park_api_v2_handler=self.park_api_v2_handler,
            ),
        )


class ParkApiV2BaseMethodView(PublicApiBaseMethodView):
    park_api_v2_handler: ParkApiV2Handler

    def __init__(self, *, park_api_v2_handler: ParkApiV2Handler, **kwargs):
        super().__init__(**kwargs)
        self.park_api_v2_handler = park_api_v2_handler


class ParkApiV2PoolsMethodView(ParkApiV2BaseMethodView):
    @document(
        description='Get ParkApi V2 Pool.',
        path=[
            Parameter(
                'pool_id',
                schema=StringField(
                    minLength=1,
                    maxLength=256,
                    example='example-city',
                ),
            )
        ],
        response=[Response(ResponseData(park_api_v2_source_schema, park_api_v2_source_example))],
    )
    def get(self, pool_id: str):
        response = self.park_api_v2_handler.get_source_as_dict(pool_id)

        return jsonify(response)


class ParkApiV2LotsMethodView(ParkApiV2BaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    @document(
        description='Get ParkApi V2 Parking Sites.',
        query=[
            Parameter(
                'location',
                schema=ArrayField(items=DecimalField(precision=10, scale=7), minItems=2, maxItems=2),
                example='6.5,50.5',
                description='Comma separated lon and lat.',
            ),
            Parameter('radius', schema=IntegerField()),
        ],
        response=[Response(ResponseData(park_api_v2_parking_sites_schema, park_api_v2_parking_sites_example))],
    )
    def get(self):
        search_query = self.validate_query_args(self.parking_site_search_query_validator)

        response = self.park_api_v2_handler.get_parking_site_list_as_dict(search_query=search_query)

        return jsonify(response)
