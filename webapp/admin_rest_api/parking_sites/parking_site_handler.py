"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass_search_queries.pagination import PaginatedResult

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.models import ParkingSite
from webapp.repositories import ParkingSiteRepository
from webapp.services.matching_service import DuplicatedParkingSite, MatchingService
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkingSiteHandler(AdminApiBaseHandler):
    parking_site_repository: ParkingSiteRepository
    matching_service: MatchingService

    def __init__(self, *args, parking_site_repository: ParkingSiteRepository, matching_service: MatchingService, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.matching_service = matching_service

    def get_parking_sites(self, search_query: ParkingSiteSearchInput) -> PaginatedResult[ParkingSite]:
        return self.parking_site_repository.fetch_parking_sites(search_query=search_query)

    def get_parking_site(self, parking_site_id: int) -> ParkingSite:
        return self.parking_site_repository.fetch_parking_site_by_id(parking_site_id)

    def generate_duplicates(self, duplicate_ids: list[list[int]], radius: Optional[int] = None) -> list[DuplicatedParkingSite]:
        duplicate_ids: list[tuple[int, int]] = [(duplicate[0], duplicate[1]) for duplicate in duplicate_ids]

        return self.matching_service.generate_duplicates(duplicate_ids, match_radius=radius)

    def apply_duplicates(self, duplicate_ids: list[list[int]]) -> list[DuplicatedParkingSite]:
        duplicate_ids: list[tuple[int, int]] = [(duplicate[0], duplicate[1]) for duplicate in duplicate_ids]

        return self.matching_service.apply_duplicates(duplicate_ids)
