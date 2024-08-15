"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass.validators import IntegerValidator
from validataclass_search_queries.filters import SearchParamEquals
from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass


@search_query_dataclass
class ParkingSiteHistorySearchQueryInput(BaseSearchQuery):
    parking_site_id: Optional[int] = SearchParamEquals(), IntegerValidator(min_value=1)
