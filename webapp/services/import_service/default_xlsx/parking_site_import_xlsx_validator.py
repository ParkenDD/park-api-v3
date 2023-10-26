"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnyOfValidator,
    DecimalValidator,
    IntegerValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from webapp.common.validation import (
    ExcelNoneable,
    ExcelTimeValidator,
    ExtendedBooleanValidator,
    GermanDurationIntegerValidator,
    NumberCastingStringValidator,
)


@validataclass
class ParkingSiteInput:
    original_uid: str = NumberCastingStringValidator(min_length=1, max_length=256)
    name: str = StringValidator(max_length=256)
    operator_name: Optional[str] = ExcelNoneable(StringValidator(max_length=256)), Default(None)
    public_url: Optional[str] = ExcelNoneable(UrlValidator(max_length=4096)), Default(None)
    address: Optional[str] = ExcelNoneable(StringValidator(max_length=512)), Default(None)
    description: Optional[str] = ExcelNoneable(StringValidator(max_length=4096)), Default(None)

    max_stay: Optional[int] = ExcelNoneable(GermanDurationIntegerValidator()), Default(None)
    has_lighting: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    is_park_ride: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    is_supervised: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    has_fee: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    fee_description: Optional[str] = ExcelNoneable(StringValidator(max_length=4096)), Default(None)
    has_live_data: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    type: Optional[str] = ExcelNoneable(AnyOfValidator(['Parkplatz', 'Parkhaus', 'Tiefgarage', 'Am Straßenrand'])), Default(None)

    lat: Decimal = NumericValidator()
    lon: Decimal = NumericValidator()

    capacity: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    capacity_disabled: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    capacity_woman: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    capacity_charging: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    capacity_carsharing: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)

    opening_hours_is_24_7: Optional[bool] = ExcelNoneable(ExtendedBooleanValidator()), Default(None)
    opening_hours_weekday_begin: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_weekday_end: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_saturday_begin: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_saturday_end: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_sunday_begin: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_sunday_end: Optional[str] = ExcelNoneable(ExcelTimeValidator()), Default(None)
