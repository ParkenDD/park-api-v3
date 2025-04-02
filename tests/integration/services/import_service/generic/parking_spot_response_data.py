"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import ANY

from parkapi_sources.models.enums import ParkingAudience, ParkingSpotStatus, PurposeType

CREATE_PARKING_SPOT_STATIC_DATA = {
    'source_id': 1,
    'original_uid': 'demo-parking-spot',
    'name': 'Test',
    'lat': Decimal('50.0000000'),
    'lon': Decimal('10.0000000'),
    'purpose': PurposeType.CAR,
    'static_data_updated_at': datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
    'has_realtime_data': True,
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
    'geojson': {
        'type': 'Polygon',
        'coordinates': [
            [
                [50 + 0.1, 10 + 0.1],
                [50 + 0.2, 10 + 0.1],
                [50 + 0.2, 10 + 0.2],
                [50 + 0.1, 10 + 0.2],
                [50 + 0.1, 10 + 0.1],
            ],
        ],
    },
}


CREATE_PARKING_SPOT_REALTIME_DATA = {
    **CREATE_PARKING_SPOT_STATIC_DATA,
    'realtime_data_updated_at': datetime(2025, 1, 1, 1, 0, tzinfo=timezone.utc),
    'realtime_status': ParkingSpotStatus.AVAILABLE,
    'has_realtime_data': True,
}


CREATE_PARKING_SPOT_WITH_PARKING_RESTRICTIONS_DATA = {
    **CREATE_PARKING_SPOT_STATIC_DATA,
    'restricted_to': [
        {
            'hours': 'Mo-Fr 08:00-18:00',
            'max_stay': 'P6H',
            'type': ParkingAudience.DISABLED,
        },
    ],
}
