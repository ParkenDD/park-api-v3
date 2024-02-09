"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import (
    ExampleListReference,
    ExampleReference,
    Parameter,
    Response,
    ResponseData,
    Schema,
    SchemaListReference,
    SchemaReference,
    document,
)
from flask_openapi.schema import ArrayField, DecimalField, NumericField, StringField
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.models import ParkingSite
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.public_rest_api.parking_sites.parking_sites_schema import parking_site_example, parking_site_schema
from webapp.public_rest_api.sources.source_schema import source_example, source_schema
from webapp.shared.parking_site import GenericParkingSiteHandler
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkingSiteBlueprint(PublicApiBaseBlueprint):
    documented: bool = True
    parking_site_handler: GenericParkingSiteHandler

    def __init__(self):
        super().__init__('parking-sites', __name__, url_prefix='/v3/parking-sites')

        self.parking_site_handler = GenericParkingSiteHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
        )

        self.add_url_rule(
            '',
            view_func=ParkingSiteListMethodView.as_view(
                'parking-sites',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )

        self.add_url_rule(
            '/<int:parking_site_id>',
            view_func=ParkingSiteItemMethodView.as_view(
                'parking-site-by-id',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )


class ParkingSiteBaseMethodView(PublicApiBaseMethodView):
    parking_site_handler: GenericParkingSiteHandler

    def __init__(self, *, parking_site_handler: GenericParkingSiteHandler, **kwargs):
        super().__init__(**kwargs)
        self.parking_site_handler = parking_site_handler


class ParkingSiteListMethodView(ParkingSiteBaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    @document(
        description='Get Parking Sites.',
        query=[
            Parameter('source_uid', schema=StringField(), example='source-uid'),
            Parameter(
                'source_uids',
                schema=ArrayField(items=StringField()),
                example='source-uid-1,source-uid-2',
            ),
            Parameter('name', schema=StringField(), example='Bahnhof'),
            Parameter(
                'location',
                schema=ArrayField(items=DecimalField(precision=10, scale=7), minItems=2, maxItems=2),
                example='6.5,50.5',
                description='Comma separated lon and lat.',
            ),
            Parameter('radius', schema=NumericField(), description='Radius, in km', example='3.5'),
        ],
        response=[
            Response(
                ResponseData(
                    schema=SchemaListReference('ParkingSite'),
                    example=ExampleListReference('ParkingSite'),
                )
            )
        ],
        components=[
            Schema('Source', schema=source_schema, example=source_example),
            Schema('ParkingSite', schema=parking_site_schema, example=parking_site_example),
        ],
    )
    def get(self):
        search_query = self.validate_query_args(self.parking_site_search_query_validator)

        parking_sites = self.parking_site_handler.get_parking_site_list(search_query=search_query)

        parking_sites = parking_sites.map(ParkingSite.to_dict)

        return self.jsonify_paginated_response(parking_sites, search_query)


class ParkingSiteItemMethodView(ParkingSiteBaseMethodView):
    @document(
        description='Get Parking Site.',
        path=[Parameter('parking_site_id', schema=int, example=1)],
        response=[
            Response(
                ResponseData(
                    schema=SchemaReference('ParkingSite'),
                    example=ExampleReference('ParkingSite'),
                )
            )
        ],
        components=[
            Schema('Source', schema=source_schema, example=source_example),
            Schema('ParkingSite', schema=parking_site_schema, example=parking_site_example),
        ],
    )
    def get(self, parking_site_id: int):
        parking_site = self.parking_site_handler.get_parking_site_item(parking_site_id)

        return jsonify(parking_site.to_dict())
