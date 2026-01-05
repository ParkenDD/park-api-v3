"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.admin_rest_api.parking_spots.parking_spot_validators import LegacyCombinedParkingSpotInput
from webapp.common.rest.exceptions import UnauthorizedException
from webapp.models import ParkingSpot
from webapp.repositories import ParkingSpotRepository, SourceRepository
from webapp.services.import_service.generic import GenericParkingSpotImportService


class ParkingSpotHandler(AdminApiBaseHandler):
    source_repository: SourceRepository
    parking_spot_repository: ParkingSpotRepository
    generic_parking_spot_import_service: GenericParkingSpotImportService

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_spot_repository: ParkingSpotRepository,
        generic_parking_spot_import_service: GenericParkingSpotImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_spot_repository = parking_spot_repository
        self.generic_parking_spot_import_service = generic_parking_spot_import_service

    def get_parking_spot_by_id(self, parking_spot_id: int) -> ParkingSpot:
        return self.parking_spot_repository.fetch_parking_spot_by_id(
            parking_spot_id,
            include_restrictions=True,
            include_external_identifiers=True,
            include_tags=True,
            include_source=True,
        )

    def get_parking_spot_by_uid(self, source_uid: str, parking_spot_uid: str) -> ParkingSpot:
        return self.parking_spot_repository.fetch_parking_spot_by_source_uid_and_original_uid(
            source_uid=source_uid,
            original_uid=parking_spot_uid,
            include_restrictions=True,
            include_external_identifiers=True,
            include_tags=True,
            include_source=True,
        )

    def delete_parking_spot_by_id(self, source_uid: str, parking_spot_id: int):
        parking_spot = self.parking_spot_repository.fetch_parking_spot_by_id(parking_spot_id, include_source=True)

        if parking_spot.source.uid != source_uid:
            raise UnauthorizedException(message='Invalid credentials for this ParkingSpot')

        self.parking_spot_repository.delete_parking_spot(parking_spot)

    def delete_parking_spot_by_uid(self, source_uid: str, parking_spot_uid: str):
        parking_spot = self.parking_spot_repository.fetch_parking_spot_by_source_uid_and_original_uid(
            source_uid=source_uid,
            original_uid=parking_spot_uid,
            include_source=True,
        )

        if parking_spot.source.uid != source_uid:
            raise UnauthorizedException(message='Invalid credentials for this ParkingSpot')

        self.parking_spot_repository.delete_parking_spot(parking_spot)

    def upsert_parking_spot(
        self,
        source_uid: str,
        legacy_combined_parking_spot_input: LegacyCombinedParkingSpotInput,
    ) -> tuple[ParkingSpot, bool]:
        source = self.source_repository.fetch_source_by_uid(source_uid)

        parking_spot, created = self.generic_parking_spot_import_service.save_static_or_combined_parking_spot_input(
            source=source,
            parking_spot_input=legacy_combined_parking_spot_input.to_combined_parking_spot_input(),
        )

        return parking_spot, created
