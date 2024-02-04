"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default
from validataclass.validators import DecimalValidator, ListValidator, StringValidator
from validataclass_search_queries.filters import (
    SearchParamContains,
    SearchParamCustom,
    SearchParamEquals,
    SearchParamMultiSelect,
)
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass

from webapp.common.validation.list_validators import CommaSeparatedListValidator


@search_query_dataclass
class ParkingSiteSearchInput(BaseSearchQuery):
    source_uid: Optional[str] = SearchParamEquals(), StringValidator()
    source_uids: Optional[str] = SearchParamMultiSelect(), ListValidator(StringValidator())
    name: Optional[str] = SearchParamContains(), StringValidator()
    location: Optional[list[Decimal, Decimal]] = SearchParamCustom(), CommaSeparatedListValidator(DecimalValidator())
    radius: Optional[Decimal] = (
        SearchParamCustom(),
        DecimalValidator(),
        Default(Decimal(100)),
    )
