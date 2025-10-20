"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

from parkapi_sources.models import OpeningStatus, RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType

from webapp.models import ParkingSite


def get_static_parking_site_input(**kwargs) -> StaticParkingSiteInput:
    default_data = {
        'uid': 'demo-parking-spot',
        'name': 'Test',
        'type': 'ON_STREET',
        'capacity': 10,
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

    return StaticParkingSiteInput(**data)


def get_realtime_parking_site_input(**kwargs) -> RealtimeParkingSiteInput:
    default_data = {
        'uid': 'demo-parking-spot',
        'realtime_data_updated_at': datetime(2025, 1, 1, 1, tzinfo=timezone.utc),
        'realtime_opening_status': OpeningStatus.OPEN,
        'realtime_free_capacity': 5,
    }

    data = deepcopy(default_data)
    data.update(**kwargs)

    return RealtimeParkingSiteInput(**data)


def get_parking_site(**kwargs) -> ParkingSite:
    base_data = {
        'original_uid': 'demo-parking-site',
        'name': 'Demo Parking Site',
        'operator_name': 'Demo Operator',
        'address': 'Demo Address, Demo City',
        'description': 'Demo Description',
        'has_realtime_data': False,
        'type': ParkingSiteType.CAR_PARK,
        'purpose': PurposeType.CAR,
        'has_fee': False,
        'lat': Decimal('50.0'),
        'lon': Decimal('10.0'),
        'opening_hours': 'Mo-Su 08:00-18:00',
        'capacity': 100,
        'static_data_updated_at': datetime.now(tz=timezone.utc),
    }

    data = deepcopy(base_data)
    data.update(**kwargs)

    return ParkingSite(**data)


def get_parking_site_by_counter(counter: int, **kwargs) -> ParkingSite:
    return get_parking_site(
        original_uid=f'demo-parking-site-{counter}',
        name=f'Demo Parking Site {counter}',
        lat=Decimal('50.0') + Decimal('0.1') * counter,
        lon=Decimal('10.0') + Decimal('0.1') * counter,
        **kwargs,
    )
