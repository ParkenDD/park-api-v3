"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from validataclass.exceptions import ValidationError
from validataclass.validators import IntegerValidator, NumericValidator, StringValidator
from validataclass_search_queries.filters import SearchParamCustom, SearchParamEquals, SearchParamMultiSelect
from validataclass_search_queries.pagination import CursorPaginationMixin
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass
from validataclass_search_queries.validators import MultiSelectValidator


@search_query_dataclass
class ParkingSpotSearchInput(CursorPaginationMixin, BaseSearchQuery):
    source_id: Optional[int] = SearchParamEquals(), IntegerValidator(allow_strings=True)
    parking_site_id: Optional[int] = SearchParamEquals(), IntegerValidator(allow_strings=True)
    source_uid: Optional[str] = SearchParamEquals(), StringValidator()
    source_uids: Optional[list[str]] = SearchParamMultiSelect(), MultiSelectValidator(StringValidator(min_length=1))

    lat: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    lon: Optional[Decimal] = SearchParamCustom(), NumericValidator()
    radius: Optional[int] = SearchParamCustom(), IntegerValidator(allow_strings=True)

    def __post_init__(self):
        if (self.lat is not None or self.lon is not None or self.radius is not None) and not (
            (self.lat and self.lon) and self.radius
        ):
            raise ValidationError(reason='lat, lon and radius have all to be set if one is set')
