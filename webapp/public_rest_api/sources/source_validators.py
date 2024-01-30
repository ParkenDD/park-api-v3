"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.search_queries import BaseSearchQuery, search_query_dataclass


@search_query_dataclass
class SourceSearchQueryInput(BaseSearchQuery):
    pass
