"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models import ParkingSiteHistory
from webapp.repositories import BaseRepository


class ParkingSiteHistoryRepository(BaseRepository):
    model_cls = ParkingSiteHistory

    def fetch_parking_site_history(self, *, search_query: Optional[BaseSearchQuery] = None) -> PaginatedResult[ParkingSiteHistory]:
        query = self.session.query(ParkingSiteHistory)

        return self._search_and_paginate(query, search_query)

    def save_parking_site_history(self, parking_site_history: ParkingSiteHistory, *, commit: bool = True):
        self._save_resources(parking_site_history, commit=commit)
