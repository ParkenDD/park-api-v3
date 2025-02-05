"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from parkapi_sources.models.enums import PurposeType
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
    SearchParamMultiSelect,
)
from validataclass_search_queries.pagination import CursorPaginationMixin, PaginationLimitValidator
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass
from validataclass_search_queries.validators import MultiSelectIntegerValidator, MultiSelectValidator

from webapp.common.validation.list_validators import CommaSeparatedListValidator


@search_query_dataclass
class ParkingSiteBaseSearchInput(CursorPaginationMixin, BaseSearchQuery):
    source_id: Optional[int] = SearchParamEquals(), IntegerValidator()
    not_source_ids: Optional[list[int]] = SearchParamCustom(), MultiSelectIntegerValidator(min_value=1)
    source_uid: Optional[str] = SearchParamEquals(), StringValidator()
    source_uids: Optional[list[str]] = SearchParamMultiSelect(), MultiSelectValidator(StringValidator(min_length=1))
    name: Optional[str] = SearchParamContains(), StringValidator()
    ignore_duplicates: bool = SearchParamCustom(), BooleanValidator(allow_strings=True), Default(True)
    purpose: Optional[PurposeType] = SearchParamEquals(), EnumValidator(PurposeType)
    limit: Optional[int] = PaginationLimitValidator(max_value=1000), Default(None)


@search_query_dataclass
class ParkingSiteSearchInput(ParkingSiteBaseSearchInput):
    lat: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    lon: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    # radius: Optional[Decimal] = SearchParamCustom(), IntegerValidator(allow_strings=True)

    # TODO: delete these two compatibility fields and enable radius above after a few weeks of adaption time: issue #134
    location: Optional[list[Decimal, Decimal]] = SearchParamCustom(), CommaSeparatedListValidator(NumericValidator())
    radius: Optional[Decimal] = SearchParamCustom(), NumericValidator()

    def __post_init__(self):
        if (self.lat is not None or self.lon is not None or self.radius is not None or self.location) and not (
            ((self.lat and self.lon) or self.location) and self.radius
        ):
            raise ValidationError(reason='lat, lon and radius have all to be set if one is set')
