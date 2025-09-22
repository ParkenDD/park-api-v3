"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from validataclass.dataclasses import Default
from validataclass.exceptions import ValidationError
from validataclass.validators import (
    BooleanValidator,
    EnumValidator,
    IntegerValidator,
    NumericValidator,
    StringValidator,
)
from validataclass_search_queries.filters import (
    SearchParamContains,
    SearchParamCustom,
    SearchParamEquals,
    SearchParamIsNotNone,
    SearchParamMultiSelect,
    SearchParamSince,
    SearchParamUntil,
)
from validataclass_search_queries.pagination import CursorPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass
from validataclass_search_queries.validators import MultiSelectIntegerValidator, MultiSelectValidator

from webapp.common.validation import DateTimeToUtcValidator
from webapp.common.validation.list_validators import CommaSeparatedListValidator


@search_query_dataclass
class ParkingSiteBaseSearchInput(BaseSearchQuery):
    source_id: int | None = SearchParamEquals(), IntegerValidator(allow_strings=True)
    source_uid: str | None = SearchParamEquals(), StringValidator()
    purpose: PurposeType | None = SearchParamEquals(), EnumValidator(PurposeType)
    type: ParkingSiteType | None = SearchParamEquals(), EnumValidator(ParkingSiteType)
    is_duplicate: bool | None = (
        SearchParamIsNotNone('duplicate_of_parking_site_id'),
        BooleanValidator(allow_strings=True),
    )


@search_query_dataclass
class ParkingSiteSearchInput(ParkingSiteBaseSearchInput, CursorPaginationMixin):
    not_source_ids: list[int] | None = SearchParamCustom(), MultiSelectIntegerValidator(min_value=1)
    source_uids: list[str] | None = SearchParamMultiSelect(), MultiSelectValidator(StringValidator(min_length=1))
    name: str | None = SearchParamContains(), StringValidator()
    ignore_duplicates: bool = SearchParamCustom(), BooleanValidator(allow_strings=True), Default(True)
    not_type: ParkingSiteType | None = SearchParamCustom(), EnumValidator(ParkingSiteType)
    limit: int | None = PaginationLimitValidator(max_value=1000), Default(None)
    static_data_updated_at_since: datetime | None = SearchParamSince('static_data_updated_at'), DateTimeToUtcValidator()
    static_data_updated_at_until: datetime | None = SearchParamUntil('static_data_updated_at'), DateTimeToUtcValidator()
    realtime_data_updated_at_since: datetime | None = (
        SearchParamSince('realtime_data_updated_at'),
        DateTimeToUtcValidator(),
    )
    realtime_data_updated_at_until: datetime | None = (
        SearchParamUntil('realtime_data_updated_at'),
        DateTimeToUtcValidator(),
    )


@search_query_dataclass
class ParkingSiteGeoSearchInput(ParkingSiteSearchInput):
    lat: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    lon: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    # radius: Optional[Decimal] = SearchParamCustom(), IntegerValidator(allow_strings=True)

    # TODO: delete these two compatibility fields and enable radius above after a few weeks of adaption time: issue #134
    location: Optional[list[Decimal]] = SearchParamCustom(), CommaSeparatedListValidator(NumericValidator())
    radius: Optional[Decimal] = SearchParamCustom(), NumericValidator()

    def __post_init__(self):
        if (self.lat is not None or self.lon is not None or self.radius is not None or self.location) and not (
            ((self.lat and self.lon) or self.location) and self.radius
        ):
            raise ValidationError(reason='lat, lon and radius have all to be set if one is set')
