"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import ANY

PARK_API_V1_INDEX_RESPONSE = {
    'api_version': '1.0',
    'server_version': '3.0.0',
    'reference': 'https://github.com/ParkenDD/park-api-v3',
    'cities': {'source-1': 'source-1', 'source-2': 'source-2', 'source-3': 'source-3'},
}

PARK_API_V1_POOL_RESPONSE = {
    'lots': [
        {
            'coords': {'lat': 50.1, 'lng': 10.1},
            'lot_type': 'garage',
            'name': 'Demo Parking Site 1',
            'original_uid': 1,
            'total': 100,
            'opening_hours': 'Mo-Su 08:00-18:00',
            'address': 'Demo Address, Demo City',
            'state': 'open',
        },
        {
            'coords': {'lat': 50.2, 'lng': 10.2},
            'lot_type': 'garage',
            'name': 'Demo Parking Site 2',
            'original_uid': 2,
            'total': 100,
            'opening_hours': 'Mo-Su 08:00-18:00',
            'address': 'Demo Address, Demo City',
            'state': 'open',
        },
        {
            'coords': {'lat': 50.3, 'lng': 10.3},
            'lot_type': 'garage',
            'name': 'Demo Parking Site 3',
            'original_uid': 3,
            'total': 100,
            'opening_hours': 'Mo-Su 08:00-18:00',
            'address': 'Demo Address, Demo City',
            'state': 'open',
        },
    ],
    'last_updated': ANY,
    'last_downloaded': ANY,
}
