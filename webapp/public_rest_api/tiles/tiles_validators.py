"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import BooleanValidator, EnumValidator, IntegerValidator, StringValidator
from validataclass_search_queries.validators import MultiSelectValidator


@validataclass
class TileFilterInput:
    purpose: PurposeType | None = EnumValidator(PurposeType), Default(None)
    types: list[ParkingSiteType] | None = MultiSelectValidator(EnumValidator(ParkingSiteType)), Default(None)
    source_uids: list[str] | None = MultiSelectValidator(StringValidator(min_length=1)), Default(None)
    ignore_duplicates: bool = BooleanValidator(allow_strings=True), Default(True)
    hide_on_street_until_zoom: int | None = IntegerValidator(min_value=0, allow_strings=True), Default(None)
