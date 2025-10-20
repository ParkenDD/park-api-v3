"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import traceback
from datetime import datetime, timezone

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import (
    ParkingAudience,
    ParkingSiteRestrictionInput,
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
)

from webapp.common.logging.models import LogMessageType
from webapp.models import ParkingSite, ParkingSiteHistory, Source
from webapp.models.parking_site_group import ParkingSiteGroup
from webapp.models.source import SourceStatus
from webapp.repositories import ParkingSiteGroupRepository, ParkingSiteHistoryRepository, ParkingSiteRepository
from webapp.repositories.exceptions import ObjectNotFoundException

from .generic_base_import_service import GenericBaseImportService

logger = logging.getLogger(__name__)

RESTRICTION_MAPPING: dict[ParkingAudience, str] = {
    ParkingAudience.DISABLED: 'capacity_disabled',
    ParkingAudience.WOMEN: 'capacity_woman',
    ParkingAudience.FAMILY: 'capacity_family',
    ParkingAudience.CHARGING: 'capacity_charging',
    ParkingAudience.CARSHARING: 'capacity_carsharing',
    ParkingAudience.TRUCK: 'capacity_truck',
    ParkingAudience.BUS: 'capacity_bus',
}


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
            except Exception as e:
                logger.warning(
                    f'Unhandled exception at dataset {static_parking_site_input}: {e} {traceback.format_exc()}',
                    extra={'attributes': {'type': LogMessageType.STATIC_PARKING_SITE_HANDLING}},
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
            if key in ['uid', 'external_identifiers', 'restrictions', 'tags', 'group_uid']:
                continue
            if (
                history_enabled
                and ('capacity' in key or key == 'realtime_opening_status')
                and getattr(parking_site, key) != value
            ):
                history_changed = True
            setattr(parking_site, key, value)

        self.set_related_objects(parking_site_input, parking_site)

        # Legacy mapping
        for restriction_input in parking_site_input.restrictions:
            if restriction_input.type not in RESTRICTION_MAPPING:
                continue
            setattr(parking_site, RESTRICTION_MAPPING[restriction_input.type], restriction_input.capacity)

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

        for realtime_parking_site_input in realtime_parking_site_inputs:
            try:
                self._save_realtime_parking_site_input(source, realtime_parking_site_input)
            except ObjectNotFoundException:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        message=f'Parking site with uid {realtime_parking_site_input.uid} available in database',
                        source_uid=source.uid,
                        data=realtime_parking_site_input.to_dict(),
                    ),
                )
            except Exception as e:
                logger.warning(
                    f'Unhandled exception at dataset {realtime_parking_site_input}: {e} {traceback.format_exc()}',
                    extra={'attributes': {'type': LogMessageType.REALTIME_PARKING_SITE_HANDLING}},
                )
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        message=f'Unhandled exception at dataset {realtime_parking_site_input}: '
                        f'{e} {traceback.format_exc()}',
                        source_uid=source.uid,
                        data=realtime_parking_site_input.to_dict(),
                    ),
                )

        if len(realtime_parking_site_inputs):
            source.realtime_status = SourceStatus.ACTIVE
        elif len(realtime_parking_site_errors):
            source.realtime_status = SourceStatus.FAILED

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_parking_site_error_count = len(realtime_parking_site_errors)

        self.source_repository.save_source(source)

    def _save_realtime_parking_site_input(self, source: Source, realtime_parking_site_input: RealtimeParkingSiteInput):
        parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
            source_id=source.id,
            original_uid=realtime_parking_site_input.uid,
            include_restrictions=True,
        )

        # Legacy mapping
        restrictions_by_audience: dict[ParkingAudience, ParkingSiteRestrictionInput] = {
            item.type: item for item in realtime_parking_site_input.restrictions
        }
        for restriction in parking_site.restrictions:
            if restriction.type is None or restriction.type not in restrictions_by_audience:
                continue

            restriction.realtime_capacity = restrictions_by_audience[restriction.type].realtime_capacity
            restriction.realtime_free_capacity = restrictions_by_audience[restriction.type].realtime_free_capacity

        for restriction in realtime_parking_site_input.restrictions:
            if restriction.type is None or restriction.type not in RESTRICTION_MAPPING:
                continue
            setattr(
                realtime_parking_site_input,
                f'realtime_{RESTRICTION_MAPPING[restriction.type]}_capacity',
                restriction.realtime_capacity,
            )
            setattr(
                realtime_parking_site_input,
                f'realtime_{RESTRICTION_MAPPING[restriction.type]}_free_capacity',
                restriction.realtime_free_capacity,
            )

        """
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
                    setattr(realtime_parking_site_input, f'realtime_free_{capacity_field}', parking_site_capacity)
                    logger.warning(
                        f'At item uid {parking_site.original_uid} from source {source.uid}, '
                        f'realtime_free_{capacity_field} {realtime_free_capacity} '
                        f'was higher than {capacity_field} {parking_site_capacity}',
                        extra={'attributes': {'type': LogMessageType.REALTIME_PARKING_SITE_HANDLING}},
                    )

            if realtime_capacity is not None:
                if realtime_free_capacity > realtime_capacity:
                    setattr(realtime_parking_site_input, f'realtime_free_{capacity_field}', realtime_capacity)
                    logger.warning(
                        f'At item uid {parking_site.original_uid} from source {source.uid}, '
                        f'realtime_free_{capacity_field} {realtime_free_capacity} '
                        f'was higher than realtime_{capacity_field} {realtime_capacity}',
                        extra={'attributes': {'type': LogMessageType.REALTIME_PARKING_SITE_HANDLING}},
                    )
        """
        history_enabled: bool = self.config_helper.get('HISTORY_ENABLED', False)
        history_changed = False
        for key, value in realtime_parking_site_input.to_dict().items():
            if key in ['uid', 'restrictions']:
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
