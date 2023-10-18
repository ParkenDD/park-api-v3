"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnyOfValidator,
    BooleanValidator,
    FloatToDecimalValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
    UrlValidator,
)


@validataclass
class LotInfoInput:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(max_length=256)
    type: Optional[str] = Noneable(AnyOfValidator(['bus', 'garage', 'level', 'lot', 'street', 'underground', 'unknown'])), Default(None)
    public_url: Optional[str] = Noneable(UrlValidator(max_length=4096)), Default(None)
    source_url: Optional[str] = Noneable(UrlValidator(max_length=4096)), Default(None)
    address: Optional[str] = Noneable(StringValidator(max_length=512, multiline=True)), Default(None)
    capacity: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    has_live_capacity: bool = Noneable(BooleanValidator()), Default(None)
    latitude: Decimal = FloatToDecimalValidator(allow_strings=True)
    longitude: Decimal = FloatToDecimalValidator(allow_strings=True)


@validataclass
class LotDataInput:
    id: str = StringValidator(min_length=1, max_length=256)
    status: Optional[str] = AnyOfValidator(['open', 'closed', 'unknown', 'nodata', 'error'])
    num_free: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    num_occupied: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
