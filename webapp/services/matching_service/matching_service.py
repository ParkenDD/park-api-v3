"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import math
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Optional

from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType
from pyproj import Geod

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
    distance: float
    name: str
    capacity: int
    api_url: str
    type: Optional[ParkingSiteType]
    park_and_ride_type: Optional[list[ParkAndRideType]]
    address: Optional[str]
    description: Optional[str]
    photo_url: Optional[str]
    public_url: Optional[str]
    opening_hours: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


class MatchingService(BaseService):
    parking_site_repository: ParkingSiteRepository
    geo_distance_service = Geod(ellps='WGS84')

    def __init__(self, *args, parking_site_repository: ParkingSiteRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository

    def generate_duplicates(
        self,
        existing_matches: list[tuple[int, int]],
        match_radius: int | None = None,
        source_ids: list[int] | None = None,
    ) -> list[DuplicatedParkingSite]:
        matches: list[tuple[ParkingSiteLocation, ParkingSiteLocation, float]] = []
        if match_radius is None:
            match_radius: int = self.config_helper.get('MATCH_RADIUS', 100)

        parking_site_locations = self.parking_site_repository.fetch_parking_site_locations(source_ids=source_ids)
        for i in range(len(parking_site_locations)):
            for j in range(i + 1, len(parking_site_locations)):
                # If both datasets are from the same source: ignore possible match
                if parking_site_locations[i].source_id == parking_site_locations[j].source_id:
                    continue

                # Duplicates should have same purpose
                if parking_site_locations[i].purpose != parking_site_locations[j].purpose:
                    continue

                # If the combination in this order is in existing matches: ignore that match
                if (parking_site_locations[i].id, parking_site_locations[j].id) in existing_matches:
                    continue

                # If distance is over match radius: ignore possible match
                distance = self.distance(parking_site_locations[i], parking_site_locations[j])
                if math.isnan(distance) or distance > match_radius:
                    continue
                matches.append((parking_site_locations[i], parking_site_locations[j], distance))

        duplicates: list[DuplicatedParkingSite] = []
        parking_site_ids: list[int] = list(set([match[0].id for match in matches] + [match[1].id for match in matches]))
        parking_sites = self.parking_site_repository.fetch_parking_site_by_ids(parking_site_ids)
        parking_sites_by_id: dict[int, ParkingSite] = {parking_site.id: parking_site for parking_site in parking_sites}

        for match in matches:
            duplicates.append(self.parking_site_to_duplicate(parking_sites_by_id[match[0].id], match[1].id, match[2]))
            duplicates.append(self.parking_site_to_duplicate(parking_sites_by_id[match[1].id], match[0].id, match[2]))

        return duplicates

    def apply_duplicates(self, duplicates: list[tuple[int, int]]):
        for parking_site_id, duplicate_parking_site_id in duplicates:
            parking_site = self.parking_site_repository.fetch_parking_site_by_id(parking_site_id)
            duplicate_parking_site = self.parking_site_repository.fetch_parking_site_by_id(duplicate_parking_site_id)
            duplicate_parking_site.duplicate_of_parking_site_id = parking_site.id
            self.parking_site_repository.save_parking_site(duplicate_parking_site)

    def parking_site_to_duplicate(
        self,
        parking_site: ParkingSite,
        duplicate_id: int,
        distance: float,
    ) -> DuplicatedParkingSite:
        return DuplicatedParkingSite(
            id=parking_site.id,
            duplicate_id=duplicate_id,
            status='KEEP',
            source_id=parking_site.source_id,
            source_uid=parking_site.source.uid,
            lat=parking_site.lat,
            lon=parking_site.lon,
            distance=distance,
            address=parking_site.address,
            capacity=parking_site.capacity,
            name=parking_site.name,
            api_url=f'{self.config_helper.get("PROJECT_URL")}/api/public/v3/parking-sites/{parking_site.id}',
            type=parking_site.type,
            park_and_ride_type=parking_site.park_and_ride_type,
            description=parking_site.description,
            photo_url=parking_site.photo_url,
            public_url=parking_site.public_url,
            opening_hours=parking_site.opening_hours,
        )

    def distance(self, location_1: ParkingSiteLocation, location_2: ParkingSiteLocation) -> float:
        _, _, distance = self.geo_distance_service.inv(
            float(location_1.lat),
            float(location_1.lon),
            float(location_2.lat),
            float(location_2.lon),
        )
        return distance
