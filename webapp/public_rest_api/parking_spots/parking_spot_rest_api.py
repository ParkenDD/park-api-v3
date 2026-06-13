"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import (
    ExampleListReference,
    ExampleReference,
    Parameter,
    Response,
    ResponseData,
    SchemaListReference,
    SchemaReference,
    document,
)
from flask_openapi.schema import ArrayField, BooleanField, IntegerField, NumericField, StringField
from validataclass.validators import BooleanValidator, DataclassValidator

from webapp.dependencies import dependencies
from webapp.models import ParkingSpot
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.shared.parking_restriction.parking_restriction_schema import parking_spot_restriction_component
from webapp.shared.parking_spot.parking_spot_schema import parking_spot_component
from webapp.shared.sources.source_schema import source_component

from .parking_spot_handler import ParkingSpotHandler
from .parking_spot_validators import ParkingSpotSearchInput


class ParkingSpotBlueprint(PublicApiBaseBlueprint):
    documented: bool = True
    parking_spot_handler: ParkingSpotHandler

    def __init__(self):
        super().__init__('parking-spots', __name__, url_prefix='/v3/parking-spots')

        self.parking_spot_handler = ParkingSpotHandler(
            **self.get_base_handler_dependencies(),
            parking_spot_repository=dependencies.get_parking_spot_repository(),
        )

        self.add_url_rule(
            '',
            view_func=ParkingSpotListMethodView.as_view(
                'parking-sites',
                **self.get_base_method_view_dependencies(),
                parking_spot_handler=self.parking_spot_handler,
            ),
        )

        self.add_url_rule(
            '/<int:parking_spot_id>',
            view_func=ParkingSpotItemMethodView.as_view(
                'parking-site-by-id',
                **self.get_base_method_view_dependencies(),
                parking_spot_handler=self.parking_spot_handler,
            ),
        )


class ParkingSpotBaseMethodView(PublicApiBaseMethodView):
    parking_spot_handler: ParkingSpotHandler
    calculate_has_realtime_data_validator = BooleanValidator(allow_strings=True)

    def __init__(self, *, parking_spot_handler: ParkingSpotHandler, **kwargs):
        super().__init__(**kwargs)
        self.parking_spot_handler = parking_spot_handler

    def _get_calculate_has_realtime_data(self) -> bool:
        # Defaults to True. If set to false, the has_realtime_data outdating calculation is skipped and the raw
        # has_realtime_data value is returned.
        raw_value = self.request_helper.get_query_args(skip_empty=True).get('calculate_has_realtime_data')
        if raw_value is None:
            return True
        return self.calculate_has_realtime_data_validator.validate(raw_value)

    def _map_parking_spot(self, parking_spot: ParkingSpot, *, calculate_has_realtime_data: bool = True) -> dict:
        unset_realtime_after_minutes = None
        if calculate_has_realtime_data:
            unset_realtime_after_minutes = self.config_helper.get('UNSET_REALTIME_AFTER_MINUTES', 30)

        return parking_spot.to_dict(
            include_restrictions=True,
            include_external_identifiers=True,
            include_tags=True,
            unset_realtime_after_minutes=unset_realtime_after_minutes,
        )


class ParkingSpotListMethodView(ParkingSpotBaseMethodView):
    parking_spot_search_query_validator = DataclassValidator(ParkingSpotSearchInput)

    @document(
        description=(
            'Get Parking Spots. This endpoint is paginated, which means that you can set a limit and iterate over '
            'pages. To maintain consistency at all situations, especially if datasets get deleted, we decided to do '
            'cursor pagination instead of offset pagination.'
        ),
        query=[
            Parameter('source_uid', schema=StringField(), example='source-uid'),
            Parameter(
                'source_uids',
                schema=ArrayField(items=StringField()),
                example='source-uid-1,source-uid-2',
            ),
            Parameter('lat', schema=NumericField(), example=55.5),
            Parameter('lon', schema=NumericField(), example=55.5),
            Parameter('radius', schema=NumericField(), description='Radius, in m', example='3500'),
            Parameter('limit', schema=IntegerField(), description='Limit results'),
            Parameter('start', schema=IntegerField(), description='Start of search query.'),
            Parameter('lat_min', schema=NumericField(), example=55.0, description='Bounding box'),
            Parameter('lat_max', schema=NumericField(), example=55.5, description='Bounding box'),
            Parameter('lon_min', schema=NumericField(), example=5.0, description='Bounding box'),
            Parameter('lon_max', schema=NumericField(), example=5.5, description='Bounding box'),
            Parameter('official_region_code', schema=StringField(maxLength=36), example='083110000000'),
            Parameter(
                'calculate_has_realtime_data',
                schema=BooleanField(),
                description='Defaults to true, which keeps the default behaviour of marking outdated realtime data as '
                'has_realtime_data=false and dropping its realtime fields. If set to false, this calculation is '
                'skipped and the raw has_realtime_data value is returned.',
            ),
        ],
        response=[
            Response(
                ResponseData(
                    schema=SchemaListReference('ParkingSpot'),
                    example=ExampleListReference('ParkingSpot'),
                )
            )
        ],
        components=[source_component, parking_spot_component, parking_spot_restriction_component],
    )
    def get(self):
        search_query = self.validate_query_args(self.parking_spot_search_query_validator)
        calculate_has_realtime_data = self._get_calculate_has_realtime_data()

        parking_spots = self.parking_spot_handler.get_parking_spot_list(search_query=search_query)

        parking_spots = parking_spots.map(
            lambda parking_spot: self._map_parking_spot(
                parking_spot,
                calculate_has_realtime_data=calculate_has_realtime_data,
            ),
        )

        return self.jsonify_paginated_response(parking_spots, search_query)


class ParkingSpotItemMethodView(ParkingSpotBaseMethodView):
    @document(
        description='Get Parking Spot.',
        path=[Parameter('parking_spot_id', schema=int, example=1)],
        query=[
            Parameter(
                'calculate_has_realtime_data',
                schema=BooleanField(),
                description='Defaults to true, which keeps the default behaviour of marking outdated realtime data as '
                'has_realtime_data=false and dropping its realtime fields. If set to false, this calculation is '
                'skipped and the raw has_realtime_data value is returned.',
            ),
        ],
        response=[
            Response(
                ResponseData(
                    schema=SchemaReference('ParkingSpot'),
                    example=ExampleReference('ParkingSpot'),
                )
            )
        ],
        components=[source_component, parking_spot_component, parking_spot_restriction_component],
    )
    def get(self, parking_spot_id: int):
        parking_spot = self.parking_spot_handler.get_parking_spot_item(parking_spot_id)

        return jsonify(
            self._map_parking_spot(
                parking_spot,
                calculate_has_realtime_data=self._get_calculate_has_realtime_data(),
            ),
        )
