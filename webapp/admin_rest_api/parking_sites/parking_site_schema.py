"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Request, Response, ResponseData
from flask_openapi.schema import (
    ArrayField,
    DecimalField,
    EnumField,
    IntegerField,
    JsonSchema,
    NumericField,
    ObjectField,
    StringField,
    UriField,
)
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType

generate_parking_site_duplicates_request_schema = JsonSchema(
    title='Apply ParkingSite duplicates request',
    properties={
        'old_duplicates': ArrayField(
            items=ArrayField(
                items=IntegerField(),
                minItems=2,
                maxItems=2,
            ),
            required=False,
        ),
        'radius': IntegerField(minimum=1, required=False, description='Radius in meters'),
        'source_ids': ArrayField(items=IntegerField(minimum=1), required=False),
        'source_uids': ArrayField(items=StringField(minLength=1), required=False),
    },
)

generate_parking_site_duplicates_request_example = {
    'radius': 25000,
}


generate_parking_site_duplicates_request = Request(
    generate_parking_site_duplicates_request_schema,
    generate_parking_site_duplicates_request_example,
)


generate_parking_site_duplicates_response_schema = JsonSchema(
    title='Apply ParkingSite duplicates response',
    properties={
        'items': ArrayField(
            items=ObjectField(
                properties={
                    'id': IntegerField(minimum=1),
                    'duplicate_id': IntegerField(minimum=1),
                    'status': StringField(),
                    'source_id': IntegerField(minimum=1),
                    'source_uid': StringField(),
                    'lat': DecimalField(precision=10, scale=7),
                    'lon': DecimalField(precision=10, scale=7),
                    'distance': NumericField(),
                    'name': StringField(),
                    'capacity': IntegerField(),
                    'api_url': UriField(),
                    'type': EnumField(enum=ParkingSiteType, nullable=True),
                    'park_and_ride_type': ArrayField(items=EnumField(enum=ParkAndRideType), nullable=True),
                    'address': StringField(nullable=True),
                    'description': StringField(nullable=True),
                    'photo_url': UriField(nullable=True),
                    'public_url': UriField(nullable=True),
                    'opening_hours': StringField(nullable=True),
                },
            ),
        ),
        'total_count': IntegerField(minimum=0),
    },
)


generate_parking_site_duplicates_response_example = {}


generate_parking_site_duplicates_response = Response(
    ResponseData(
        generate_parking_site_duplicates_response_schema,
        generate_parking_site_duplicates_response_example,
    ),
)


apply_parking_site_duplicates_request_schema = JsonSchema(
    title='Apply ParkingSite duplicates request',
    properties={
        'ignore': ArrayField(
            items=ArrayField(
                items=IntegerField(),
                minItems=2,
                maxItems=2,
            ),
        ),
        'keep': ArrayField(
            items=ArrayField(
                items=IntegerField(),
                minItems=2,
                maxItems=2,
            ),
        ),
    },
)


apply_parking_site_duplicates_request_example = {
    'ignore': [
        [1, 2],
        [3, 4],
    ],
    'keep': [
        [1, 5],
        [2, 6],
    ],
}


apply_parking_site_duplicates_request = Request(
    apply_parking_site_duplicates_request_schema,
    apply_parking_site_duplicates_request_example,
)
