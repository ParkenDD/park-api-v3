"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

from parkapi_sources.models import RealtimeParkingSpotInput, StaticParkingSpotInput
from parkapi_sources.models.enums import PurposeType

from webapp.models import ParkingSpot
from webapp.models.parking_spot import ParkingSpotStatus


def get_parking_spot(**kwargs) -> ParkingSpot:
    base_data = {
        'original_uid': 'demo-parking-spot',
        'name': 'Test',
        'realtime_status': ParkingSpotStatus.AVAILABLE,
        'purpose': PurposeType.CAR,
        'has_realtime_data': True,
        'lat': Decimal('50.0'),
        'lon': Decimal('10.0'),
        'static_data_updated_at': datetime.now(timezone.utc),
        'realtime_data_updated_at': datetime.now(timezone.utc),
    }

    # Because of @hybrid_property limitations, we cannot set geojson at init, so we handle that after init
    if 'geojson' in kwargs:
        geojson = kwargs.pop('geojson')
    else:
        geojson = {
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
        }

    data = deepcopy(base_data)
    data.update(**kwargs)

    parking_spot = ParkingSpot(**data)

    parking_spot.geojson = geojson

    return parking_spot


def get_parking_spot_by_counter(counter: int, **kwargs) -> ParkingSpot:
    return get_parking_spot(
        original_uid=f'demo-parking-spot-{counter}',
        lat=Decimal('50.0') + Decimal('0.1') * counter,
        lon=Decimal('10.0') + Decimal('0.1') * counter,
        geojson={
            'type': 'Polygon',
            'coordinates': [
                [
                    [round(50 + 0.1 * counter, 2), round(10 + 0.1 * counter, 2)],
                    [round(50 + 0.1 + 0.1 * counter, 2), round(10 + 0.1 * counter, 2)],
                    [round(50 + 0.1 + 0.1 * counter, 2), round(10 + 0.1 + 0.1 * counter, 2)],
                    [round(50 + 0.1 * counter, 2), round(10 + 0.1 + 0.1 * counter, 2)],
                    [round(50 + 0.1 * counter, 2), round(10 + 0.1 * counter, 2)],
                ],
            ],
        },
        **kwargs,
    )


def get_static_parking_spot_input(**kwargs) -> StaticParkingSpotInput:
    default_data = {
        'uid': 'demo-parking-spot',
        'name': 'Test',
        'purpose': PurposeType.CAR,
        'static_data_updated_at': datetime(2025, 1, 1, tzinfo=timezone.utc),
        'has_realtime_data': True,
        'lat': Decimal('50.0'),
        'lon': Decimal('10.0'),
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

    data = deepcopy(default_data)
    data.update(**kwargs)

    return StaticParkingSpotInput(**data)


def get_static_parking_spot_input_by_counter(counter: int, **kwargs) -> StaticParkingSpotInput:
    return get_static_parking_spot_input(
        uid=f'demo-parking-spot-{counter}',
        lat=Decimal('50.0') + Decimal('0.1') * counter,
        lon=Decimal('10.0') + Decimal('0.1') * counter,
        geojson={
            'type': 'Polygon',
            'coordinates': [
                [
                    [50 + 0.1 * counter, 10 + 0.1 * counter],
                    [50 + 0.1 + 0.1 * counter, 10 + 0.1 * counter],
                    [50 + 0.1 + 0.2 * counter, 10 + 0.1 + 0.2 * counter],
                    [50 + 0.1 * counter, 10 + 0.1 + 0.2 * counter],
                    [50 + 0.1 * counter, 10 + 0.1 * counter],
                ],
            ],
        },
        **kwargs,
    )


def get_realtime_parking_spot_input(**kwargs) -> RealtimeParkingSpotInput:
    default_data = {
        'uid': 'demo-parking-spot',
        'realtime_data_updated_at': datetime(2025, 1, 1, 1, tzinfo=timezone.utc),
        'realtime_status': ParkingSpotStatus.AVAILABLE,
    }

    data = deepcopy(default_data)
    data.update(**kwargs)

    return RealtimeParkingSpotInput(**data)


def get_realtime_parking_spot_input_by_counter(counter: int, **kwargs) -> RealtimeParkingSpotInput:
    return get_realtime_parking_spot_input(
        uid=f'demo-parking-spot-{counter}',
        realtime_status=ParkingSpotStatus.AVAILABLE if counter % 1 else ParkingSpotStatus.TAKEN,
        **kwargs,
    )
