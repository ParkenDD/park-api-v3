"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.schema import (
    ArrayField,
    BooleanField,
    DateTimeField,
    DecimalField,
    EnumField,
    IntegerField,
    JsonSchema,
    StringField,
    UriField,
)

from webapp.models.parking_site import ParkAndRideType, ParkingSiteType

parking_site_schema = JsonSchema(
    title='ParkingSite',
    properties={
        'id': IntegerField(),
        'created_at': DateTimeField(),
        'modified_at': DateTimeField(),
        'source_id': IntegerField(minimum=1),
        'original_uid': StringField(maxLength=256),
        'name': StringField(maxLength=256),
        'operator_name': StringField(maxLength=256, required=False),
        'public_url': UriField(maxLength=4096, required=False),
        'address': StringField(maxLength=512, required=False),
        'description': StringField(maxLength=4096, required=False),
        'type': EnumField(enum=ParkingSiteType),
        'max_stay': IntegerField(minimum=0, required=False),
        'max_height': IntegerField(minimum=0, required=False),
        'has_lighting': BooleanField(required=False),
        'park_and_ride_type': ArrayField(items=EnumField(enum=ParkAndRideType), required=False),
        'is_supervised': BooleanField(required=False),
        'has_realtime_data': BooleanField(default=False),
        'static_data_updated_at': DateTimeField(),
        'realtime_opening_status': DateTimeField(required=False),
        'lat': DecimalField(precision=10, scale=7),
        'lon': DecimalField(precision=10, scale=7),
        'capacity': IntegerField(minimum=0),
        'capacity_disabled': IntegerField(minimum=0, required=False),
        'capacity_woman': IntegerField(minimum=0, required=False),
        'capacity_family': IntegerField(minimum=0, required=False),
        'capacity_charging': IntegerField(minimum=0, required=False),
        'capacity_carsharing': IntegerField(minimum=0, required=False),
        'capacity_truck': IntegerField(minimum=0, required=False),
        'capacity_bus': IntegerField(minimum=0, required=False),
        'realtime_capacity': IntegerField(minimum=0, required=False),
        'realtime_capacity_disabled': IntegerField(minimum=0, required=False),
        'realtime_capacity_woman': IntegerField(minimum=0, required=False),
        'realtime_capacity_family': IntegerField(minimum=0, required=False),
        'realtime_capacity_charging': IntegerField(minimum=0, required=False),
        'realtime_capacity_carsharing': IntegerField(minimum=0, required=False),
        'realtime_capacity_truck': IntegerField(minimum=0, required=False),
        'realtime_capacity_bus': IntegerField(minimum=0, required=False),
        'realtime_free_capacity': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_disabled': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_woman': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_family': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_charging': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_carsharing': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_truck': IntegerField(minimum=0, required=False),
        'realtime_free_capacity_bus': IntegerField(minimum=0, required=False),
        'opening_hours': StringField(maxLength=512, required=False, description='OSM opening_hours format'),
    },
)

parking_site_example = {}
