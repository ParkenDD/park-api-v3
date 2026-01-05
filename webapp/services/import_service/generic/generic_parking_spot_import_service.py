"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import traceback
from datetime import datetime, timezone

from parkapi_sources import ParkAPISources
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import RealtimeParkingSpotInput, StaticParkingSpotInput

from webapp.common.logging.models import LogMessageType
from webapp.models import ParkingSpot, Source
from webapp.models.source import SourceStatus
from webapp.repositories import (
    ParkingSiteRepository,
    ParkingSpotRepository,
    SourceRepository,
)
from webapp.repositories.exceptions import ObjectNotFoundException

from .generic_base_import_service import GenericBaseImportService

logger = logging.getLogger(__name__)


class GenericParkingSpotImportService(GenericBaseImportService):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository
    parking_spot_repository: ParkingSpotRepository
    park_api_sources: ParkAPISources

    def __init__(
        self,
        *args,
        parking_site_repository: ParkingSiteRepository,
        parking_spot_repository: ParkingSpotRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.parking_spot_repository = parking_spot_repository

    def handle_static_import_results(
        self,
        source: Source,
        static_parking_spot_inputs: list[StaticParkingSpotInput],
        static_parking_spot_errors: list[ImportParkingSpotException],
    ):
        existing_parking_spot_ids = self.parking_spot_repository.fetch_parking_spot_ids_by_source_id(source.id)
        for static_parking_spot_input in static_parking_spot_inputs:
            try:
                self.save_static_or_combined_parking_spot_input(
                    source,
                    static_parking_spot_input,
                    existing_parking_spot_ids,
                )
            except Exception as e:
                logger.warning(
                    f'Unhandled exception at dataset {static_parking_spot_input}: {e} {traceback.format_exc()}',
                    extra={'attributes': {'type': LogMessageType.STATIC_PARKING_SPOT_HANDLING}},
                )

        # Delete remaining existing parking sites because they are not in the new dataset
        for existing_parking_spot_id in existing_parking_spot_ids:
            existing_parking_spot = self.parking_spot_repository.fetch_parking_spot_by_id(existing_parking_spot_id)
            self.parking_spot_repository.delete_parking_spot(existing_parking_spot)

        if len(static_parking_spot_inputs):
            source.static_status = SourceStatus.ACTIVE
        elif len(static_parking_spot_errors):
            source.realtime_status = SourceStatus.FAILED

        source.static_data_updated_at = datetime.now(tz=timezone.utc)
        source.static_parking_spot_error_count = len(static_parking_spot_errors)

        self.source_repository.save_source(source)

        logger.info(
            f'Successfully imported {len(static_parking_spot_inputs)} static parking spots from {source.uid}, '
            f'and ignored {len(static_parking_spot_errors)} datasets with errors.',
            extra={'attributes': {'type': LogMessageType.STATIC_PARKING_SPOT_HANDLING}},
        )

    def save_static_or_combined_parking_spot_input(
        self,
        source: Source,
        parking_spot_input: StaticParkingSpotInput,
        existing_parking_spot_ids: list[int] | None = None,
    ) -> tuple[ParkingSpot, bool]:
        try:
            parking_spot = self.parking_spot_repository.fetch_parking_spot_by_source_id_and_original_uid(
                source_id=source.id,
                original_uid=parking_spot_input.uid,
            )
            created = False
            # If the ParkingSpot exists: remove it from existing parking site list
            if existing_parking_spot_ids is not None and parking_spot.id in existing_parking_spot_ids:
                existing_parking_spot_ids.remove(parking_spot.id)
        except ObjectNotFoundException:
            parking_spot = ParkingSpot()
            parking_spot.source_id = source.id
            parking_spot.original_uid = parking_spot_input.uid
            created = True

        for key, value in parking_spot_input.to_dict().items():
            if key in [
                'uid',
                'external_identifiers',
                'restrictions',
                'tags',
                'parking_site_uid',
            ]:
                continue
            setattr(parking_spot, key, value)

        self.set_related_objects(parking_spot_input, parking_spot)

        if parking_spot_input.parking_site_uid:
            try:
                parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_original_uid(
                    source_id=source.id,
                    original_uid=parking_spot_input.parking_site_uid,
                )
                parking_spot.parking_site = parking_site
            except ObjectNotFoundException:
                parking_spot.parking_site_id = None
        else:
            parking_spot.parking_site_id = None

        self.parking_spot_repository.save_parking_spot(parking_spot)

        return parking_spot, created

    def handle_realtime_import_results(
        self,
        source: Source,
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput],
        realtime_parking_spot_errors: list[ImportParkingSpotException],
    ):
        if source.static_status != SourceStatus.ACTIVE:
            return

        for realtime_parking_spot_input in realtime_parking_spot_inputs:
            try:
                self.save_realtime_parking_spot_input(source, realtime_parking_spot_input)
            except ObjectNotFoundException:
                realtime_parking_spot_errors.append(
                    ImportParkingSpotException(
                        message=f'Parking spot with uid {realtime_parking_spot_input.uid} available in database',
                        source_uid=source.uid,
                        data=realtime_parking_spot_input.to_dict(),
                    ),
                )
            except Exception as e:
                logger.warning(
                    f'Unhandled exception at dataset {realtime_parking_spot_input}: {e} {traceback.format_exc()}',
                    extra={'attributes': {'type': LogMessageType.REALTIME_PARKING_SPOT_HANDLING}},
                )
                realtime_parking_spot_errors.append(
                    ImportParkingSpotException(
                        message=f'Unhandled exception at dataset {realtime_parking_spot_input}: '
                        f'{e} {traceback.format_exc()}',
                        source_uid=source.uid,
                        data=realtime_parking_spot_input.to_dict(),
                    ),
                )

        if len(realtime_parking_spot_inputs):
            source.realtime_status = SourceStatus.ACTIVE
        elif len(realtime_parking_spot_errors):
            source.realtime_status = SourceStatus.FAILED

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_parking_spot_error_count = len(realtime_parking_spot_errors)

        self.source_repository.save_source(source)

        logger.info(
            f'Successfully imported {len(realtime_parking_spot_inputs)} realtime parking spots from {source.uid}, '
            f'and ignored {len(realtime_parking_spot_errors)} datasets with errors.',
            extra={'attributes': {'type': LogMessageType.REALTIME_PARKING_SPOT_HANDLING}},
        )

    def save_realtime_parking_spot_input(self, source: Source, realtime_parking_spot_input: RealtimeParkingSpotInput):
        parking_spot = self.parking_spot_repository.fetch_parking_spot_by_source_id_and_original_uid(
            source_id=source.id,
            original_uid=realtime_parking_spot_input.uid,
        )

        for key, value in realtime_parking_spot_input.to_dict().items():
            if key == 'uid':
                continue
            setattr(parking_spot, key, value)

        self.parking_spot_repository.save_parking_spot(parking_spot)
