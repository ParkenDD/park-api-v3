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
from flask_openapi.schema import ArrayField, BooleanField, EnumField, IntegerField, NumericField, StringField
from parkapi_sources.models.enums import PurposeType
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.public_rest_api.parking_sites.parking_sites_schema import parking_site_example, parking_site_schema
from webapp.public_rest_api.sources.source_schema import source_example, source_schema
from webapp.shared.parking_site.generic_parking_site_handler import GenericParkingSiteHandler
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
        description='Get Parking Sites. This endpoint is paginated, which means that you can set a limit and iterate over pages. To '
        'maintain consistency at all situations, especially if datasets get deleted, we decided to do cursor pagination '
        'instead of offset pagination.',
        query=[
            Parameter('source_uid', schema=StringField(), example='source-uid'),
            Parameter(
                'source_uids',
                schema=ArrayField(items=StringField()),
                example='source-uid-1,source-uid-2',
            ),
            Parameter('name', schema=StringField(), example='Bahnhof'),
            Parameter('lat', schema=NumericField(), example=55.5),
            Parameter('lon', schema=NumericField(), example=55.5),
            Parameter('radius', schema=NumericField(), description='Radius, in m', example='3500'),
            Parameter('limit', schema=IntegerField(), description='Limit results'),
            Parameter('start', schema=IntegerField(), description='Start of search query.'),
            Parameter('purpose', schema=EnumField(enum=PurposeType)),
            Parameter(
                'ignore_duplicates',
                schema=BooleanField(),
                description='Defaults to true. If set to false, you will get ParkingSites flagged as duplicates, too.',
            ),
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

        parking_sites = parking_sites.map(lambda item: item.to_dict(include_external_identifiers=True, include_tags=True))

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

        return jsonify(parking_site.to_dict(include_external_identifiers=True, include_tags=True))
