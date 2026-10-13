"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.models import CombinedParkingSiteInput
from parkapi_sources.models.enums import PurposeType
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
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
