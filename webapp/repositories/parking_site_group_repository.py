"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models.parking_site_group import ParkingSiteGroup
from webapp.repositories import BaseRepository


class ParkingSiteGroupRepository(BaseRepository):
    model_cls = ParkingSiteGroup

    def fetch_parking_site_group(
        self,
        *,
        search_query: Optional[BaseSearchQuery] = None,
    ) -> PaginatedResult[ParkingSiteGroup]:
        query = self.session.query(ParkingSiteGroup)

        return self._search_and_paginate(query, search_query)

    def fetch_parking_site_group_by_id(self, parking_site_group_id: int) -> ParkingSiteGroup:
        return self.fetch_resource_by_id(parking_site_group_id)

    def fetch_parking_site_group_by_original_uid(self, parking_site_group_uid: str) -> ParkingSiteGroup:
        parking_site_group = (
            self.session.query(ParkingSiteGroup).filter(ParkingSiteGroup.original_uid == parking_site_group_uid).first()
        )

        return self._or_raise(parking_site_group, f'ParkingSiteGroup with {parking_site_group_uid} does not exist')

    def save_parking_site_group(self, parking_site_group: ParkingSiteGroup, *, commit: bool = True):
        self._save_resources(parking_site_group, commit=commit)
