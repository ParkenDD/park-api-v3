"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import traceback
from datetime import datetime, timezone

from parkapi_sources import ParkAPISources
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import RealtimeParkingSpotInput, StaticParkingSpotInput
from webapp.common.logging.models import LogMessageType
from webapp.models import ParkingRestriction, ParkingSpot, Source
from webapp.models.source import SourceStatus
from webapp.repositories import (
    ParkingSpotRepository,
    SourceRepository,
)
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService


class GenericParkingSpotImportService(BaseService):
    source_repository: SourceRepository
    parking_spot_repository: ParkingSpotRepository
    park_api_sources: ParkAPISources

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_spot_repository: ParkingSpotRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
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
                self._save_static_parking_spot_input(source, static_parking_spot_input, existing_parking_spot_ids)
            except:
                self.logger.warning(
                    LogMessageType.FAILED_STATIC_SOURCE_HANDLING,
                    f'Unhandled exception at dataset {static_parking_spot_input}: {traceback.format_exc()}',
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

    def _save_static_parking_spot_input(
        self,
        source: Source,
        static_parking_spot_input: StaticParkingSpotInput,
        existing_parking_spot_ids: list[int],
    ):
        try:
            parking_spot = self.parking_spot_repository.fetch_parking_spot_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=static_parking_spot_input.uid,
            )
            # If the ParkingSpot exists: remove it from existing parking site list
            if parking_spot.id in existing_parking_spot_ids:
                existing_parking_spot_ids.remove(parking_spot.id)
        except ObjectNotFoundException:
            parking_spot = ParkingSpot()
            parking_spot.source_id = source.id
            parking_spot.original_uid = static_parking_spot_input.uid

        for key, value in static_parking_spot_input.to_dict().items():
            if key in ['uid', 'restricted_to']:
                continue
            setattr(parking_spot, key, value)

        if static_parking_spot_input.restricted_to is not None:
            parking_restrictions: list[ParkingRestriction] = []
            for i, parking_restrictions_input in enumerate(static_parking_spot_input.restricted_to):
                if len(static_parking_spot_input.restricted_to) < len(parking_spot.restricted_to):
                    parking_restriction = parking_spot.restricted_to[i]
                else:
                    parking_restriction = ParkingRestriction()

                parking_restriction.from_dict(parking_restrictions_input.to_dict())

                parking_restrictions.append(parking_restriction)
            parking_spot.restricted_to = parking_restrictions
        else:
            parking_spot.restricted_to = []

        self.parking_spot_repository.save_parking_spot(parking_spot)

    def handle_realtime_import_results(
        self,
        source: Source,
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput],
        realtime_parking_spot_errors: list[ImportParkingSpotException],
    ):
        if source.static_status != SourceStatus.ACTIVE:
            return

        realtime_parking_spot_error_count = len(realtime_parking_spot_errors)

        for realtime_parking_spot_input in realtime_parking_spot_inputs:
            try:
                self._save_realtime_parking_spot_input(source, realtime_parking_spot_input)
            except ObjectNotFoundException:
                realtime_parking_spot_error_count += 1
            except:
                realtime_parking_spot_error_count += 1
                self.logger.warning(
                    LogMessageType.FAILED_REALTIME_SOURCE_HANDLING,
                    f'Unhandled exception at dataset {realtime_parking_spot_input}: {traceback.format_exc()}',
                )

        if len(realtime_parking_spot_inputs):
            source.realtime_status = SourceStatus.ACTIVE
        elif realtime_parking_spot_error_count:
            source.realtime_status = SourceStatus.FAILED

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_parking_spot_error_count = realtime_parking_spot_error_count

        self.source_repository.save_source(source)

    def _save_realtime_parking_spot_input(self, source: Source, realtime_parking_spot_input: RealtimeParkingSpotInput):
        parking_spot = self.parking_spot_repository.fetch_parking_spot_by_source_id_and_external_uid(
            source_id=source.id,
            original_uid=realtime_parking_spot_input.uid,
        )

        for key, value in realtime_parking_spot_input.to_dict().items():
            if key == 'uid':
                continue
            setattr(parking_spot, key, value)

        self.parking_spot_repository.save_parking_spot(parking_spot)
