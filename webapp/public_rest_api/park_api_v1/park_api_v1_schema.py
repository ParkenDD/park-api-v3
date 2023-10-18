"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.schema import (
    AnyOfField,
    ArrayField,
    BooleanField,
    DateTimeField,
    IntegerField,
    JsonSchema,
    NumericField,
    ObjectField,
    StringField,
    UriField,
)

park_api_v1_sources_schema = JsonSchema(
    title='ParkAPI V1 Sources Response',
    properties={
        'api_version': StringField(description='API Version. Should be 1.0.'),
        'server_version': StringField(description='Server Version. Should be 3.0+'),
        'reference': StringField(),
        'cities': ObjectField(
            properties={},
            description='An object with Names as key and source uids ans value.',
        ),
    },
)

park_api_v1_sources_example = {
    'api_version': '1.0',
    'server_version': '1.0.0',
    'reference': 'https://github.com/offenesdresden/ParkAPI',
    'cities': {
        'City 1': 'city1id',
        'City 2': 'city2id',
    },
}


park_api_v1_parking_site_schema = JsonSchema(
    title='ParkAPI V1 Parking Sites Response',
    properties={
        'lots': ArrayField(
            items=ObjectField(
                description='A parking site / parking lot is an area with multiple parking places.',
                properties={
                    'coords': ObjectField(
                        properties={
                            'lat': NumericField(),
                            'lon': NumericField(),
                        },
                    ),
                    'forecast': BooleanField(
                        description='If the data source offers a forecast. Is not available at this service and documented just for compatibility reasons.'
                    ),
                    'lot_type': AnyOfField(
                        allowed_values=['street', 'lot', 'underground', 'garage'],
                        required=False,
                    ),
                    'name': StringField(minLength=1, maxLength=256),
                    'id': StringField(
                        description='Unique identifier within a source',
                        minLength=1,
                        maxLength=256,
                    ),
                    'capacity': IntegerField(description='Capacity including all used sparking spots and without longterm parking spots.'),
                    'public_url': UriField(required=False),
                    'opening_hours': StringField(required=False, description='In OSM opening_hours format'),
                    'fee_hours': StringField(
                        required=False,
                        description='In OSM opening_hours format. Is not available at this service and documented just for compatibility reasons.',
                    ),
                    'address': StringField(
                        required=False,
                        description='Contains a full address with street, house number, postcode and address',
                    ),
                    'free': IntegerField(required=False),
                    'status': AnyOfField(allowed_values=['open', 'closed', 'nodata', 'unknown']),
                },
            ),
        ),
        'last_updated': DateTimeField(required=False),
        'last_downloaded': DateTimeField(required=False),
        'data_source': UriField(required=False),
    },
)

park_api_v1_parking_site_example = {
    'last_updated': '2015-06-15T12:31:00',
    'last_downloaded': '2015-06-15T12:31:25',
    'data_source': 'http://examplecity.com',
    'lots': [
        {
            'coords': {
                'lat': 51.05031,
                'lng': 13.73754,
            },
            'name': 'Altmarkt',
            'total': 400,
            'free': 235,
            'state': 'open',
            'id': 'lot_id',
            'forecast': False,
            'region': 'Region X',
            'address': 'Musterstraße 5',
            'lot_type': 'Parkhaus',
            'opening_hours': '24/7',
            'url': 'https://examplecity.com/parken/Altmarkt',
        },
    ],
}
