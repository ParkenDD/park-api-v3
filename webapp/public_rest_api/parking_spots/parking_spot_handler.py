"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.pagination import PaginatedResult

from webapp.models import ParkingSpot
from webapp.public_rest_api.base_handler import PublicApiBaseHandler
from webapp.public_rest_api.parking_spots.parking_spot_validators import ParkingSpotSearchInput
from webapp.repositories import ParkingSpotRepository


class ParkingSpotHandler(PublicApiBaseHandler):
    def __init__(self, *args, parking_spot_repository: ParkingSpotRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_spot_repository = parking_spot_repository

    def get_parking_spot_list(self, search_query: ParkingSpotSearchInput) -> PaginatedResult:
        return self.parking_spot_repository.fetch_parking_spots(
            search_query=search_query,
            include_restricted_to=True,
            include_external_identifiers=True,
            include_tags=True,
        )

    def get_parking_spot_item(self, parking_spot_id: int) -> ParkingSpot:
        return self.parking_spot_repository.fetch_parking_spot_by_id(
            parking_spot_id,
            include_restricted_to=True,
            include_external_identifiers=True,
            include_tags=True,
        )
