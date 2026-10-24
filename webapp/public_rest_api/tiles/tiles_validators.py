"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.models.enums import PurposeType
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import BooleanValidator, EnumValidator


@validataclass
class TileFilterInput:
    purpose: PurposeType | None = EnumValidator(PurposeType), Default(None)
    ignore_duplicates: bool = BooleanValidator(allow_strings=True), Default(True)
