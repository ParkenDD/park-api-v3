"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy

from parkapi_sources.models import ParkingRestrictionInput
from parkapi_sources.models.enums import ParkingAudience

from webapp.models import ParkingRestriction


def get_parking_restriction(**kwargs) -> ParkingRestriction:
    base_data = {
        'type': ParkingAudience.DISABLED,
        'hours': 'Mo-Fr 08:00-18:00',
        'max_stay': 'P6H',
    }

    data = deepcopy(base_data)
    data.update(**kwargs)

    return ParkingRestriction(**data)


def get_parking_restriction_input(**kwargs) -> ParkingRestrictionInput:
    base_data = {
        'type': ParkingAudience.DISABLED,
        'hours': 'Mo-Fr 08:00-18:00',
        'max_stay': 'P6H',
    }

    data = deepcopy(base_data)
    data.update(**kwargs)

    return ParkingRestrictionInput(**data)
