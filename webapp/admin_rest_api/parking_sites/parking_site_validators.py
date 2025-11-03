"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import fields
from typing import Any

from parkapi_sources.models import CombinedParkingSiteInput, ParkingAudience, ParkingSiteRestrictionInput
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import AnythingValidator, IntegerValidator, ListValidator, Noneable, StringValidator

CAPACITY_TYPES: dict[str, ParkingAudience] = {
    'disabled': ParkingAudience.DISABLED,
    'woman': ParkingAudience.WOMEN,
    'family': ParkingAudience.FAMILY,
    'charging': ParkingAudience.CHARGING,
    'carsharing': ParkingAudience.CARSHARING,
    'truck': ParkingAudience.TRUCK,
    'bus': ParkingAudience.BUS,
}


@validataclass
class LegacyCombinedParkingSiteInput(CombinedParkingSiteInput):
    capacity_disabled: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_woman: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_family: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_charging: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_truck: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_bus: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    realtime_capacity_disabled: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_woman: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_family: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_charging: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_capacity_truck: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_bus: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    realtime_free_capacity_disabled: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_woman: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_family: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_charging: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_truck: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_bus: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )

    def to_combined_parking_site_input(self) -> CombinedParkingSiteInput:
        combined_parking_site_dict: dict[str, Any] = {}
        # prevent recursive dataclass to dict by using fields
        for field in fields(self):
            key = field.name
            if key.endswith(tuple(CAPACITY_TYPES.keys())):
                continue

            combined_parking_site_dict[key] = getattr(self, key)

        combined_parking_site_input = CombinedParkingSiteInput(**combined_parking_site_dict)

        for key, audience in CAPACITY_TYPES.items():
            if getattr(self, f'capacity_{key}') is not None:
                combined_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(
                        type=audience,
                        capacity=getattr(self, f'capacity_{key}'),
                        realtime_capacity=getattr(self, f'realtime_capacity_{key}'),
                        realtime_free_capacity=getattr(self, f'realtime_free_capacity_{key}'),
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
