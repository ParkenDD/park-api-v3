"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.pagination import PaginatedResult

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.admin_rest_api.parking_sites.parking_site_validators import GetDuplicatesInput
from webapp.models import ParkingSite
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.services.matching_service import DuplicatedParkingSite, MatchingService
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkingSiteHandler(AdminApiBaseHandler):
    parking_site_repository: ParkingSiteRepository
    source_repository: SourceRepository
    matching_service: MatchingService

    def __init__(
        self,
        *args,
        parking_site_repository: ParkingSiteRepository,
        matching_service: MatchingService,
        source_repository: SourceRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.source_repository = source_repository
        self.matching_service = matching_service

    def get_parking_sites(self, search_query: ParkingSiteSearchInput) -> PaginatedResult[ParkingSite]:
        return self.parking_site_repository.fetch_parking_sites(search_query=search_query)

    def get_parking_site(self, parking_site_id: int) -> ParkingSite:
        return self.parking_site_repository.fetch_parking_site_by_id(parking_site_id)

    def generate_duplicates(self, duplicate_input: GetDuplicatesInput) -> list[DuplicatedParkingSite]:
        duplicate_ids: list[tuple[int, int]] = [
            (duplicate[0], duplicate[1]) for duplicate in duplicate_input.old_duplicates
        ]
        if duplicate_input.source_ids is not None:
            source_ids = duplicate_input.source_ids
        elif duplicate_input.source_uids is not None:
            source_ids = self.source_repository.fetch_source_ids_by_source_uids(duplicate_input.source_uids)
        else:
            source_ids = None

        return self.matching_service.generate_duplicates(
            duplicate_ids,
            match_radius=duplicate_input.radius,
            source_ids=source_ids,
        )

    def apply_duplicates(self, duplicate_ids: list[list[int]]) -> list[DuplicatedParkingSite]:
        duplicate_ids: list[tuple[int, int]] = [(duplicate[0], duplicate[1]) for duplicate in duplicate_ids]

        return self.matching_service.apply_duplicates(duplicate_ids)
