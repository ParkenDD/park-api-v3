"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Request, Response, ResponseData
from flask_openapi.schema import (
    ArrayField,
    BooleanField,
    DateTimeField,
    DecimalField,
    EnumField,
    IntegerField,
    JsonSchema,
    NumericField,
    ObjectField,
    Reference,
    StringField,
    UriField,
)
from parkapi_sources.models.enums import (
    ExternalIdentifierType,
    OpeningStatus,
    ParkAndRideType,
    ParkingSiteType,
    PurposeType,
    SupervisionType,
)

parking_site_item_request_schema = JsonSchema(
    title='ParkingSite Request',
    properties={
        'capacity': IntegerField(minimum=0, nullable=True),
        'capacity_disabled': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_woman': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_family': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_charging': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_carsharing': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_truck': IntegerField(minimum=0, required=False, nullable=True),
        'capacity_bus': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_disabled': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_woman': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_family': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_charging': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_carsharing': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_truck': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_capacity_bus': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_disabled': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_woman': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_family': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_charging': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_carsharing': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_truck': IntegerField(minimum=0, required=False, nullable=True),
        'realtime_free_capacity_bus': IntegerField(minimum=0, required=False, nullable=True),
        'uid': StringField(maxLength=256, description='Unique Identifier.'),
        'purpose': EnumField(enum=PurposeType),
        'photo_url': UriField(maxLength=4096, required=False, nullable=True, description='Photo of the parking site'),
        'name': StringField(maxLength=256),
        'operator_name': StringField(maxLength=256, required=False, nullable=True),
        'public_url': UriField(
            maxLength=4096,
            required=False,
            nullable=True,
            description='URL for human users to get more details about this parking site.',
        ),
        'address': StringField(
            maxLength=512,
            required=False,
            nullable=True,
            description='Full address including street postalcode and city. Preferable in format {street with number}, {postalcode} {city}',
        ),
        'description': StringField(
            maxLength=4096,
            required=False,
            nullable=True,
            description='Description for customers like special conditions, remarks how to get there etc.',
        ),
        'type': EnumField(
            enum=ParkingSiteType,
            description='ON_STREET, OFF_STREET_PARKING_GROUND, UNDERGROUND and CAR_PARK are used at car parks, '
            'WALL_LOOPS, STANDS, LOCKERS, SHED, TWO_TIER, BUILDING are used at bike parks, and OTHER at both.',
        ),
        'max_stay': IntegerField(minimum=0, required=False, nullable=True, description='Maximum stay, in seconds.'),
        'max_height': IntegerField(minimum=0, required=False, nullable=True, description='Max height, in centimeters.'),
        'has_lighting': BooleanField(required=False, nullable=True),
        'park_and_ride_type': ArrayField(items=EnumField(enum=ParkAndRideType), required=False, nullable=True),
        'supervision_type': EnumField(enum=SupervisionType, required=False),
        'is_covered': BooleanField(required=False),
        'related_location': StringField(maxLength=256, required=False, description='A related location like a school.'),
        'has_realtime_data': BooleanField(default=False),
        'fee_description': StringField(required=False),
        'has_fee': BooleanField(required=False),
        'static_data_updated_at': DateTimeField(
            description='Last time static fields were updated.',
        ),
        'realtime_data_updated_at': DateTimeField(
            required=False,
            description='Last time realtime fields were updated. Required if `has_realtime_data` is true.',
        ),
        'realtime_opening_status': EnumField(
            enum=OpeningStatus,
            required=False,
            description='Realtime opening status which is reported by the client.',
        ),
        'lat': DecimalField(precision=10, scale=7),
        'lon': DecimalField(precision=10, scale=7),
        'external_identifiers': ArrayField(
            items=ObjectField(
                properties={
                    'type': EnumField(enum=ExternalIdentifierType),
                    'value': StringField(maxLength=256),
                },
            ),
            required=False,
        ),
        'tags': ArrayField(items=StringField(maxLength=256), required=False),
        'opening_hours': StringField(maxLength=512, required=False, description='OSM opening_hours format'),
    },
)


parking_site_item_request = Request(schema=parking_site_item_request_schema)


parking_site_list_request_schema = JsonSchema(
    title='ParkingSite List Request',
    properties={
        'items': ArrayField(
            items=parking_site_item_request_schema,
        ),
    },
)


parking_site_list_request = Request(schema=parking_site_list_request_schema)


parking_site_list_response_schema = JsonSchema(
    title='ParkingSite List Response',
    properties={
        'items': ArrayField(
            items=Reference(obj='ParkingSite'),
        ),
        'errors': ArrayField(
            items=ObjectField(
                properties={
                    'source_uid': StringField(),
                    'parking_site_uid': StringField(nullable=True),
                    'message': StringField(),
                    'data': ObjectField(
                        properties={
                            'code': StringField(),
                            'field_errors': ObjectField(
                                properties={},
                                additionalProperties=True,
                                description='The JSON key is the field which has the validation error, the value describes the '
                                'validation error',
                            ),
                        },
                    ),
                }
            ),
        ),
    },
)

parking_site_list_response = Response(ResponseData(schema=parking_site_list_response_schema))


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
