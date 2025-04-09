"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from decimal import Decimal

from parkapi_sources.models.enums import ParkingSiteType, PurposeType

from webapp.models import ParkingSite


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
