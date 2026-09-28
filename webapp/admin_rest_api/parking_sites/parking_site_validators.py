"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import fields
from typing import Any

from parkapi_sources.models import (
    CombinedParkingSiteInput,
    ParkingRestrictionInput,
    ParkingSiteRestrictionInput,
    ParkingSpotRestrictionInput,
)
from parkapi_sources.models.enums import PurposeType
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    StringValidator,
)


@validataclass
class LegacyCombinedParkingSiteInput(CombinedParkingSiteInput):
    # parkapi-sources 0.36.0 dropped the default value for `purpose`, making it required. We keep defaulting it to
    # CAR here so existing clients that don't send a purpose keep working.
    # TODO: remove this default after a migration period so `purpose` becomes required again.
    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)

    restricted_to: list[ParkingRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingSpotRestrictionInput))),
        Default(None),
    )

    def to_combined_parking_site_input(self) -> CombinedParkingSiteInput:
        combined_parking_site_dict: dict[str, Any] = {}
        # prevent recursive dataclass to dict by using fields
        for field in fields(self):
            key = field.name
            if key == 'restricted_to':
                continue

            combined_parking_site_dict[key] = getattr(self, key)

        combined_parking_site_input = CombinedParkingSiteInput(**combined_parking_site_dict)

        if self.restricted_to is not None:
            for restriction in self.restricted_to:
                combined_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(
                        type=restriction.type,
                        hours=restriction.hours,
                        max_stay=restriction.max_stay,
                    ),
                )

        return combined_parking_site_input


@validataclass
class ParkingSiteListInput:
    items: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))


@validataclass
class GetDuplicatesInput:
    old_duplicates: list[list[int]] = (
        ListValidator(
            ListValidator(IntegerValidator(min_value=1), min_length=2, max_length=2),
        ),
        Default([]),
    )
    radius: int | None = Noneable(IntegerValidator(min_value=1)), Default(None)
    source_ids: list[int] | None = ListValidator(IntegerValidator(min_value=1)), Default(None)
    source_uids: list[str] | None = ListValidator(StringValidator(min_length=1)), Default(None)


@validataclass
class ApplyDuplicatesInput:
    ignore: list[list[int]] = ListValidator(ListValidator(IntegerValidator(), min_length=2, max_length=2))
    keep: list[list[int]] = ListValidator(ListValidator(IntegerValidator(), min_length=2, max_length=2))
