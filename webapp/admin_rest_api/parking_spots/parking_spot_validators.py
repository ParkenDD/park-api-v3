"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import fields
from typing import Any

from parkapi_sources.models import CombinedParkingSpotInput, ParkingSpotRestrictionInput
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import DataclassValidator, ListValidator, Noneable


@validataclass
class LegacyCombinedParkingSpotInput(CombinedParkingSpotInput):
    restricted_to: list[ParkingSpotRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingSpotRestrictionInput))),
        Default(None),
    )

    def to_combined_parking_spot_input(self) -> CombinedParkingSpotInput:
        combined_parking_spot_dict: dict[str, Any] = {}

        # prevent recursive dataclass to dict by using fields
        for field in fields(self):
            key = field.name
            if key == 'restricted_to':
                continue
            combined_parking_spot_dict[key] = getattr(self, key)

        combined_parking_site_input = CombinedParkingSpotInput(**combined_parking_spot_dict)

        if self.restricted_to is not None:
            combined_parking_site_input.restrictions += self.restricted_to

        return combined_parking_site_input
