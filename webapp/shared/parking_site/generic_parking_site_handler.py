"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.pagination import PaginatedResult

from webapp.models import ParkingSite
from webapp.public_rest_api.base_handler import PublicApiBaseHandler
from webapp.repositories import ParkingSiteRepository
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteBaseSearchInput


class GenericParkingSiteHandler(PublicApiBaseHandler):
    parking_site_repository: ParkingSiteRepository

    def __init__(self, *args, parking_site_repository: ParkingSiteRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository

    def get_parking_site_list(self, search_query: ParkingSiteBaseSearchInput) -> PaginatedResult[ParkingSite]:
        return self.parking_site_repository.fetch_parking_sites(
            search_query=search_query,
            include_external_identifiers=True,
            include_tags=True,
            include_parking_site_group=True,
        )

    def get_parking_site_item(self, parking_site_id: int) -> ParkingSite:
        return self.parking_site_repository.fetch_parking_site_by_id(
            parking_site_id,
            include_external_identifiers=True,
            include_tags=True,
        )
