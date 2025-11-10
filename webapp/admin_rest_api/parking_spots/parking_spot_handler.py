"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.admin_rest_api.parking_spots.parking_spot_validators import LegacyCombinedParkingSpotInput
from webapp.models import ParkingSpot
from webapp.repositories import SourceRepository
from webapp.services.import_service.generic import GenericParkingSpotImportService


class ParkingSpotHandler(AdminApiBaseHandler):
    source_repository: SourceRepository
    generic_parking_spot_import_service: GenericParkingSpotImportService

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        generic_parking_spot_import_service: GenericParkingSpotImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.generic_parking_spot_import_service = generic_parking_spot_import_service

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
