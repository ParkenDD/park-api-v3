"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from decimal import Decimal

from parkapi_sources.models.enums import PurposeType

from webapp.models import ParkingSite, Source


def get_parking_site(counter: int, source: Source | None = None, **kwargs) -> ParkingSite:
    base_data = {
        'original_uid': f'parking-site-{counter}',
        'name': f'Parking Site {counter}',
        'has_realtime_data': False,
        'purpose': PurposeType.CAR,
        'lat': Decimal('50.0') + Decimal('0.1') * counter,
        'lon': Decimal('10.0') + Decimal('0.1') * counter,
    }
    if source:
        base_data['source'] = source

    data = deepcopy(base_data)
    data.update(kwargs)

    parking_site = ParkingSite(**data)

    return parking_site
