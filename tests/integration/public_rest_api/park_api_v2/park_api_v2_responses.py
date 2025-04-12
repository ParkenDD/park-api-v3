"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import ANY

PARK_API_V2_POOL_RESPONSE = {
    'date_created': ANY,
    'date_updated': ANY,
    'pool_id': 'source-1',
    'name': 'source-1',
}

PARK_API_V2_LOTS_RESPONSE = {
    'count': 6,
    'next': None,
    'previous': None,
    'results': [
        {
            'date_created': ANY,
            'date_updated': ANY,
            'coordinates': [10.1, 50.1],
            'has_live_capacity': False,
            'pool_id': 'source-1',
            'type': 'garage',
            'lot_id': 'demo-parking-site-1',
            'name': 'Demo Parking Site 1',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
        {
            'coordinates': [10.2, 50.2],
            'has_live_capacity': False,
            'pool_id': 'source-1',
            'type': 'garage',
            'date_created': ANY,
            'date_updated': ANY,
            'lot_id': 'demo-parking-site-2',
            'name': 'Demo Parking Site 2',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
        {
            'coordinates': [10.3, 50.3],
            'has_live_capacity': False,
            'pool_id': 'source-1',
            'type': 'garage',
            'date_created': ANY,
            'date_updated': ANY,
            'lot_id': 'demo-parking-site-3',
            'name': 'Demo Parking Site 3',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
        {
            'coordinates': [10.4, 50.4],
            'has_live_capacity': False,
            'pool_id': 'source-2',
            'type': 'garage',
            'date_created': ANY,
            'date_updated': ANY,
            'lot_id': 'demo-parking-site-4',
            'name': 'Demo Parking Site 4',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
        {
            'coordinates': [10.5, 50.5],
            'has_live_capacity': False,
            'pool_id': 'source-2',
            'type': 'garage',
            'date_created': ANY,
            'date_updated': ANY,
            'lot_id': 'demo-parking-site-5',
            'name': 'Demo Parking Site 5',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
        {
            'coordinates': [10.6, 50.6],
            'has_live_capacity': False,
            'pool_id': 'source-3',
            'type': 'garage',
            'date_created': ANY,
            'date_updated': ANY,
            'lot_id': 'demo-parking-site-6',
            'name': 'Demo Parking Site 6',
            'address': 'Demo Address, Demo City',
            'max_capacity': 100,
            'latest_data': {'timestamp': ANY, 'status': ANY},
        },
    ],
}
