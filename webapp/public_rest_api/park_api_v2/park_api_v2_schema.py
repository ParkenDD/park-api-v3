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

park_api_v2_source_schema = JsonSchema(
    title='ParkAPI V2 Source Response',
    properties={
        'date_created': DateTimeField(),
        'date_updated': DateTimeField(),
        'pool_id': StringField(minLength=1, maxLength=512),
        'name': StringField(),
        'public_url': UriField(required=False, nullable=True),
        'source_url': UriField(required=False, nullable=True),
        'license': StringField(required=False, nullable=True),
    },
)


park_api_v2_source_example = {
    'date_created': '2021-11-25T11:44:03.868010',
    'date_updated': '2021-11-25T11:44:03.868027',
    'pool_id': 'apag',
    'name': 'Aachener Parkhaus GmbH',
    'public_url': 'https://www.apag.de',
    'source_url': None,
    'license': None,
}


park_api_v2_parking_sites_schema = JsonSchema(
    title='ParkAPI V2 Parking Sites Response',
    properties={
        'count': IntegerField(minimum=0),
        'next': UriField(required=False, nullable=True),
        'results': ArrayField(
            items=ObjectField(
                properties={
                    'pool_id': StringField(minLength=1, maxLength=512),
                    'coordinates': ArrayField(
                        items=NumericField(),
                        minItems=2,
                        maxItems=2,
                        description='First value is lon, second value is lat',
                    ),
                    'latest_data': ObjectField(
                        properties={
                            'timestamp': DateTimeField(),
                            'lot_timestamp': DateTimeField(),
                            'status': AnyOfField(allowed_values=['open', 'closed']),
                            'num_free': IntegerField(),
                            'capacity': IntegerField(),
                            'num_occupied': IntegerField(),
                            'percent_free': NumericField(),
                        },
                    ),
                    'date_created': DateTimeField(),
                    'date_updated': DateTimeField(),
                    'lot_id': StringField(maxLength=1),
                    'name': StringField(),
                    'address': StringField(),
                    'type': AnyOfField(allowed_values=['street', 'lot', 'underground', 'garage']),
                    'max_capacity': IntegerField(),
                    'has_live_capacity': BooleanField(),
                    'public_url': UriField(),
                    'source_url': UriField(),
                }
            )
        ),
    },
)


park_api_v2_parking_sites_example = {
    'count': 13,
    'next': None,
    'previous': None,
    'results': [
        {
            'pool_id': 'apag',
            'coordinates': [
                6.076306,
                50.767823,
            ],
            'latest_data': {
                'timestamp': '2021-11-26T10:08:30',
                'lot_timestamp': None,
                'status': 'open',
                'num_free': 6,
                'capacity': 70,
                'num_occupied': 64,
                'percent_free': 8.57,
            },
            'date_created': '2021-11-25T11:44:03.917080',
            'date_updated': '2021-11-25T16:26:37.914537',
            'lot_id': 'aachen-parkplatz-luisenhospital',
            'name': 'Luisenhospital',
            'address': 'Parkplatz Luisenhospital\nBoxgraben 99\n52064\nAachen',
            'type': 'lot',
            'max_capacity': 70,
            'has_live_capacity': False,
            'public_url': 'https://www.apag.de/parkobjekte/parkplatz-luisenhospital',
            'source_url': 'https://www.apag.de/parken-in-aachen',
        },
    ],
}
