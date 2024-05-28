"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import asdict, dataclass
from decimal import Decimal
from math import acos, cos, sin

from webapp.common.logging.models import LogMessageType
from webapp.models import ParkingSite
from webapp.repositories import ParkingSiteRepository
from webapp.repositories.parking_site_repository import ParkingSiteLocation
from webapp.services.base_service import BaseService


@dataclass
class DuplicatedParkingSite:
    id: int
    duplicate_id: int
    status: str
    source_id: int
    source_uid: str
    lat: Decimal
    lon: Decimal
    address: str
    capacity: int

    def to_dict(self) -> dict:
        return asdict(self)


class MatchingService(BaseService):
    parking_site_repository: ParkingSiteRepository

    def __init__(self, *args, parking_site_repository: ParkingSiteRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository

    def generate_duplicates(self, existing_matches: list[tuple[int, int]]) -> list[DuplicatedParkingSite]:
        matches: list[tuple[ParkingSiteLocation, ParkingSiteLocation]] = []
        match_radius: int = self.config_helper.get('MATCH_RADIUS', 100)

        parking_site_locations = self.parking_site_repository.fetch_parking_site_locations()
        for i in range(0, len(parking_site_locations)):
            for j in range(i + 1, len(parking_site_locations)):
                # If both datasets are from the same source: ignore possible match
                # if parking_site_locations[i].source_id == parking_site_locations[j].source_id:
                #    continue

                # If the combination in this order is in existing matches: ignore that match
                if (parking_site_locations[i].id, parking_site_locations[j].id) in existing_matches:
                    continue

                # If distance is over match radius: ignore possible match
                try:
                    if self.distance(parking_site_locations[i], parking_site_locations[j]) > match_radius:
                        continue
                # Ignore (and log) invalid data at distance calculations (eg 'math domain error')
                except ValueError:
                    self.logger.warning(
                        LogMessageType.DUPLICATE_HANDLING,
                        f'Cannot calculate distance between {parking_site_locations[i]} and {parking_site_locations[j]}',
                    )
                    continue

                matches.append((parking_site_locations[i], parking_site_locations[j]))

        duplicates: list[DuplicatedParkingSite] = []
        parking_site_ids: list[int] = list(set([match[0].id for match in matches] + [match[1].id for match in matches]))
        parking_sites = self.parking_site_repository.fetch_parking_site_by_ids(parking_site_ids)
        parking_sites_by_id: dict[int, ParkingSite] = {parking_site.id: parking_site for parking_site in parking_sites}

        for match in matches:
            duplicates.append(self.parking_site_to_duplicate(parking_sites_by_id[match[0].id], match[1].id))
            duplicates.append(self.parking_site_to_duplicate(parking_sites_by_id[match[1].id], match[0].id))

        return duplicates

    def apply_duplicates(self, duplicates: list[tuple[int, int]]):
        for parking_site_id, duplicate_parking_site_id in duplicates:
            parking_site = self.parking_site_repository.fetch_parking_site_by_id(parking_site_id)
            duplicate_parking_site = self.parking_site_repository.fetch_parking_site_by_id(duplicate_parking_site_id)
            duplicate_parking_site.duplicate_of_parking_site_id = parking_site.id
            self.parking_site_repository.save_parking_site(duplicate_parking_site)

    @staticmethod
    def parking_site_to_duplicate(parking_site: ParkingSite, duplicate_id: int) -> DuplicatedParkingSite:
        return DuplicatedParkingSite(
            id=parking_site.id,
            duplicate_id=duplicate_id,
            status='KEEP',
            source_id=parking_site.source_id,
            source_uid=parking_site.source.uid,
            lat=parking_site.lat,
            lon=parking_site.lon,
            address=parking_site.address,
            capacity=parking_site.capacity,
        )

    @staticmethod
    def distance(location_1: ParkingSiteLocation, location_2: ParkingSiteLocation) -> float:
        return 6371010 * acos(
            sin(location_1.lat) * sin(location_2.lat) + cos(location_1.lat) * cos(location_2.lat) * cos(location_1.lon - location_2.lon),
        )
