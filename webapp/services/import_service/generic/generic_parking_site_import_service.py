"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import traceback
from datetime import datetime, timezone

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput

from webapp.common.logging.models import LogMessageType
from webapp.models import ParkingSite, ParkingSiteHistory, Source
from webapp.models.parking_site_group import ParkingSiteGroup
from webapp.models.source import SourceStatus
from webapp.repositories import ParkingSiteGroupRepository, ParkingSiteHistoryRepository, ParkingSiteRepository
from webapp.repositories.exceptions import ObjectNotFoundException

from .generic_base_import_service import GenericBaseImportService


class GenericParkingSiteImportService(GenericBaseImportService):
    parking_site_repository: ParkingSiteRepository
    parking_site_history_repository: ParkingSiteHistoryRepository
    parking_site_group_repository: ParkingSiteGroupRepository

    def __init__(
        self,
        *args,
        parking_site_repository: ParkingSiteRepository,
        parking_site_history_repository: ParkingSiteHistoryRepository,
        parking_site_group_repository: ParkingSiteGroupRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.parking_site_history_repository = parking_site_history_repository
        self.parking_site_group_repository = parking_site_group_repository

    def handle_static_import_results(
        self,
        source: Source,
        static_parking_site_inputs: list[StaticParkingSiteInput],
        static_parking_site_errors: list[ImportParkingSiteException],
    ):
        existing_parking_site_ids = self.parking_site_repository.fetch_parking_site_ids_by_source_id(source.id)
        for static_parking_site_input in static_parking_site_inputs:
            try:
                self.save_static_or_combined_parking_site_input(
                    source,
                    static_parking_site_input,
                    existing_parking_site_ids,
                )
            except:
                self.logger.warning(
                    LogMessageType.FAILED_STATIC_SOURCE_HANDLING,
                    f'Unhandled exception at dataset {static_parking_site_input}: {traceback.format_exc()}',
                )

                # Delete remaining existing parking sites because they are not in the new dataset
        for existing_parking_site_id in existing_parking_site_ids:
            existing_parking_site = self.parking_site_repository.fetch_parking_site_by_id(existing_parking_site_id)
            self.parking_site_repository.delete_parking_site(existing_parking_site)

        if len(static_parking_site_inputs):
            source.static_status = SourceStatus.ACTIVE
        elif len(static_parking_site_errors):
            source.realtime_status = SourceStatus.FAILED

        source.static_data_updated_at = datetime.now(tz=timezone.utc)
        source.static_parking_site_error_count = len(static_parking_site_errors)

    def save_static_or_combined_parking_site_input(
        self,
        source: Source,
        parking_site_input: StaticParkingSiteInput,
        existing_parking_site_ids: list[int],
    ) -> ParkingSite:
        try:
            parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=parking_site_input.uid,
            )
            # If the ParkingSite exists: remove it from existing parking site list
            if parking_site.id in existing_parking_site_ids:
                existing_parking_site_ids.remove(parking_site.id)
        except ObjectNotFoundException:
            parking_site = ParkingSite()
            parking_site.source_id = source.id
            parking_site.original_uid = parking_site_input.uid

        history_enabled: bool = self.config_helper.get('HISTORY_ENABLED', False)
        history_changed = False
        for key, value in parking_site_input.to_dict().items():
            if key in ['uid', 'external_identifiers', 'restricted_to', 'tags', 'group_uid']:
                continue
            if (
                history_enabled
                and ('capacity' in key or key == 'realtime_opening_status')
                and getattr(parking_site, key) != value
            ):
                history_changed = True
            setattr(parking_site, key, value)

        self.set_related_objects(parking_site_input, parking_site)

        if parking_site_input.group_uid:
            try:
                parking_site_group = self.parking_site_group_repository.fetch_parking_site_group_by_original_uid(
                    parking_site_input.group_uid,
                )
            except ObjectNotFoundException:
                parking_site_group = ParkingSiteGroup()
                parking_site_group.original_uid = parking_site_input.group_uid
                parking_site_group.source_id = parking_site.source_id

            parking_site.parking_site_group = parking_site_group
        else:
            parking_site.parking_site_group_id = None

        self.parking_site_repository.save_parking_site(parking_site)
        if history_enabled and history_changed:
            self._add_history(parking_site)

        return parking_site

    def handle_realtime_import_results(
        self,
        source: Source,
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput],
        realtime_parking_site_errors: list[ImportParkingSiteException],
    ):
        if source.static_status != SourceStatus.ACTIVE:
            return

        realtime_parking_site_error_count = len(realtime_parking_site_errors)

        for realtime_parking_site_input in realtime_parking_site_inputs:
            try:
                self._save_realtime_parking_site_input(source, realtime_parking_site_input)
            except ObjectNotFoundException:
                realtime_parking_site_error_count += 1
            except:
                realtime_parking_site_error_count += 1
                self.logger.warning(
                    LogMessageType.FAILED_REALTIME_SOURCE_HANDLING,
                    f'Unhandled exception at dataset {realtime_parking_site_input}: {traceback.format_exc()}',
                )

        if len(realtime_parking_site_inputs):
            source.realtime_status = SourceStatus.ACTIVE
        elif realtime_parking_site_error_count:
            source.realtime_status = SourceStatus.FAILED

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_parking_site_error_count = realtime_parking_site_error_count

        self.source_repository.save_source(source)

    def _save_realtime_parking_site_input(self, source: Source, realtime_parking_site_input: RealtimeParkingSiteInput):
        parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
            source_id=source.id,
            original_uid=realtime_parking_site_input.uid,
        )
        capacity_fields: list[str] = [
            'capacity',
            'capacity_woman',
            'capacity_disabled',
            'capacity_charging',
            'capacity_carsharing',
            'capacity_bus',
            'capacity_family',
            'capacity_truck',
        ]

        for capacity_field in capacity_fields:
            realtime_free_capacity = getattr(realtime_parking_site_input, f'realtime_free_{capacity_field}')
            # Not all realtime datasets have free capacities
            if realtime_free_capacity is None:
                continue

            realtime_capacity = getattr(realtime_parking_site_input, f'realtime_{capacity_field}')

            parking_site_capacity = getattr(parking_site, capacity_field)
            if parking_site_capacity is None:
                continue

            if realtime_capacity is None:
                if realtime_free_capacity > parking_site_capacity:
                    setattr(realtime_parking_site_input, realtime_free_capacity, parking_site_capacity)
                    self.logger.warning(
                        LogMessageType.FAILED_PARKING_SITE_HANDLING,
                        f'At {parking_site.original_uid} from {source.id}, '
                        f'realtime_free_{capacity_field} {realtime_free_capacity} '
                        f'was higher than {capacity_field} {parking_site_capacity}',
                    )

            if realtime_capacity is not None:
                if realtime_free_capacity > realtime_capacity:
                    setattr(realtime_parking_site_input, realtime_free_capacity, realtime_capacity)
                    self.logger.warning(
                        LogMessageType.FAILED_PARKING_SITE_HANDLING,
                        f'At {parking_site.original_uid} from {source.id}, '
                        f'realtime_free_{capacity_field} {realtime_free_capacity} '
                        f'was higher than realtime_{capacity_field} {realtime_capacity}',
                    )

        history_enabled: bool = self.config_helper.get('HISTORY_ENABLED', False)
        history_changed = False
        for key, value in realtime_parking_site_input.to_dict().items():
            if key in ['uid']:
                continue
            if (
                history_enabled
                and ('capacity' in key or key == 'realtime_opening_status')
                and getattr(parking_site, key) != value
            ):
                history_changed = True
            setattr(parking_site, key, value)

        self.parking_site_repository.save_parking_site(parking_site)
        if history_enabled and history_changed:
            self._add_history(parking_site)

    def _add_history(self, parking_site: ParkingSite):
        parking_site_history = ParkingSiteHistory()
        parking_site_history.parking_site_id = parking_site.id
        for key, value in parking_site.to_dict().items():
            if 'capacity' in key or key in [
                'realtime_opening_status',
                'static_data_updated_at',
                'realtime_data_updated_at',
            ]:
                setattr(parking_site_history, key, value)
        self.parking_site_history_repository.save_parking_site_history(parking_site_history)
