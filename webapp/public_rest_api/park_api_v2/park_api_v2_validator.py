"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from typing import Optional

from validataclass.exceptions import ValidationError
from validataclass.validators import NumericValidator
from validataclass_search_queries.filters import SearchParamCustom
from validataclass_search_queries.search_queries import search_query_dataclass

from webapp.common.validation.list_validators import CommaSeparatedListValidator
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


@search_query_dataclass
class ParkApiV2SearchInput(ParkingSiteSearchInput):
    location: Optional[list[Decimal]] = SearchParamCustom(), CommaSeparatedListValidator(NumericValidator())
    radius: Optional[Decimal] = SearchParamCustom(), NumericValidator()

    def __post_init__(self):
        if (self.location is not None or self.radius is not None) and not (self.location and self.radius):
            raise ValidationError(reason='location and radius have all to be set if one is set')
