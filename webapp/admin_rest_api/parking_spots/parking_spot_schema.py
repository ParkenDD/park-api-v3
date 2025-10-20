"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Request
from flask_openapi.schema import (
    AnyOfField,
    ArrayField,
    BooleanField,
    DateTimeField,
    DecimalField,
    EnumField,
    JsonSchema,
    NumericField,
    ObjectField,
    StringField,
)
from parkapi_sources.models.enums import ParkingAudience, ParkingSpotStatus, ParkingSpotType, PurposeType

parking_spot_request_schema = JsonSchema(
    title='Parking Spot Request',
    properties={
        'uid': StringField(minLength=1, maxLength=256),
        'name': StringField(minLength=1, maxLength=256, required=False, nullable=True),
        'address': StringField(maxLength=256, required=False, nullable=True),
        'purpose': EnumField(enum=PurposeType, default=PurposeType.CAR, required=False),
        'type': EnumField(enum=ParkingSpotType, required=False, nullable=True),
        'description': StringField(maxLength=4096, required=False, nullable=True),
        'static_data_updated_at': DateTimeField(),
        'has_realtime_data': BooleanField(),
        'lat': DecimalField(precision=10, scale=7),
        'lon': DecimalField(precision=10, scale=7),
        'realtime_data_updated_at': DateTimeField(),
        'realtime_status': EnumField(enum=ParkingSpotStatus, required=False, nullable=True),
        'geojson': ObjectField(
            properties={
                'type': AnyOfField(allowed_values=['Polygon']),
                'coordinates': ArrayField(
                    items=ArrayField(
                        items=ArrayField(
                            items=NumericField(),
                            minItems=2,
                            maxItems=2,
                        ),
                    ),
                    minItems=1,
                    maxItems=1,
                ),
            },
        ),
        'restrictions': ArrayField(
            items=ObjectField(
                properties={
                    'type': EnumField(enum=ParkingAudience, required=False, nullable=True),
                    'hours': StringField(required=False, nullable=True, description='OSM OpeningTimes format'),
                    'max_stay': StringField(required=False, nullable=True, description='ISO 8601 duration'),
                },
            ),
        ),
    },
)

parking_spot_request_example = {}


parking_spot_request = Request(parking_spot_request_schema, parking_spot_request_example)
