"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.pagination import PaginatedResult

from webapp.models import ParkingSiteHistory
from webapp.public_rest_api.parking_sites.parking_sites_validators import ParkingSiteHistorySearchQueryInput
from webapp.repositories import ParkingSiteHistoryRepository
from webapp.shared.parking_site.generic_parking_site_handler import GenericParkingSiteHandler


class ParkingSiteHandler(GenericParkingSiteHandler):
    def __init__(self, *args, parking_site_history_repository: ParkingSiteHistoryRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_history_repository = parking_site_history_repository

    def get_parking_site_history_list(
        self,
        parking_site_id: int,
        search_query: ParkingSiteHistorySearchQueryInput,
    ) -> PaginatedResult[ParkingSiteHistory]:
        search_query.parking_site_id = parking_site_id

        return self.parking_site_history_repository.fetch_parking_site_history(search_query=search_query)
