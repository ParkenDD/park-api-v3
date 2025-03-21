"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import traceback
from datetime import datetime, timezone

from flask import Flask
from parkapi_sources import ParkAPISources
from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from validataclass.helpers import UnsetValue

from webapp.common.logging.models import LogMessageType, LogTag
from webapp.common.rest.exceptions import UnknownSourceException
from webapp.models import ExternalIdentifier, ParkingSite, ParkingSiteHistory, Source, Tag
from webapp.models.parking_site_group import ParkingSiteGroup
from webapp.models.source import SourceStatus
from webapp.repositories import (
    ParkingSiteGroupRepository,
    ParkingSiteHistoryRepository,
    ParkingSiteRepository,
    SourceRepository,
)
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService


class ParkingSiteGenericImportService(BaseService):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository
    parking_site_history_repository: ParkingSiteHistoryRepository
    parking_site_group_repository: ParkingSiteGroupRepository
    park_api_sources: ParkAPISources

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
        parking_site_history_repository: ParkingSiteHistoryRepository,
        parking_site_group_repository: ParkingSiteGroupRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository
        self.parking_site_history_repository = parking_site_history_repository
        self.parking_site_group_repository = parking_site_group_repository

    def init_app(self, app: Flask):
        park_api_source_uids: list[str] = []
        park_api_sources_config: dict[str, str] = {
            'STATIC_GEOJSON_BASE_URL': app.config['STATIC_GEOJSON_BASE_URL'],
            'DEBUG_DUMP_DIR': app.config['DEBUG_DUMP_DIR'],
            'DEBUG_SOURCES': app.config['DEBUG_SOURCES'],
        }
        for source_dict in app.config.get('PARK_API_CONVERTER', []):
            park_api_source_uids.append(source_dict['uid'])
            if 'env' in source_dict:
                park_api_sources_config.update(source_dict['env'])

        self.park_api_sources = ParkAPISources(
            converter_uids=park_api_source_uids,
            config=park_api_sources_config,
        )
        self.park_api_sources.check_credentials()

    def update_sources_static(self):
        for source_uid in self.park_api_sources.converter_by_uid.keys():
            if isinstance(self.park_api_sources.converter_by_uid[source_uid], PullConverter):
                self.update_source_static(source_uid)

    def update_sources_realtime(self):
        for source_uid in self.park_api_sources.converter_by_uid.keys():
            if isinstance(self.park_api_sources.converter_by_uid[source_uid], PullConverter):
                self.update_source_realtime(source_uid)

    def update_source_static(self, source_uid: str):
        self.logger.set_tag(LogTag.SOURCE, source_uid)

        source = self.get_upserted_source(source_uid)
        converter: PullConverter = self.park_api_sources.converter_by_uid[source_uid]  # type: ignore

        try:
            static_parking_site_inputs, static_parking_site_errors = converter.get_static_parking_sites()
        except Exception as e:
            self.logger.warning(message_type=LogMessageType.FAILED_STATIC_SOURCE_HANDLING, message=str(e))
            source.static_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        self.handle_static_import_results(source, static_parking_site_inputs, static_parking_site_errors)

        for static_parking_site_error in static_parking_site_errors:
            self.logger.warning(LogMessageType.FAILED_STATIC_PARKING_SITE_HANDLING, str(static_parking_site_error))

        source.static_data_updated_at = datetime.now(tz=timezone.utc)
        source.static_status = SourceStatus.ACTIVE
        self.source_repository.save_source(source)

    def update_source_realtime(self, source_uid: str):
        self.logger.set_tag(LogTag.SOURCE, source_uid)

        source = self.source_repository.fetch_source_by_uid(source_uid)
        converter: PullConverter = self.park_api_sources.converter_by_uid[source_uid]  # type: ignore

        # We can't do realtime updates when static data is not active
        if source.static_status != SourceStatus.ACTIVE:
            return

        # We don't do realtime updates if it's disabled
        if source.realtime_status == SourceStatus.DISABLED:
            return

        try:
            realtime_parking_site_inputs, realtime_parking_site_errors = converter.get_realtime_parking_sites()
        except Exception as e:
            self.logger.warning(message_type=LogMessageType.FAILED_REALTIME_SOURCE_HANDLING, message=str(e))
            source.realtime_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        self.handle_realtime_import_results(source, realtime_parking_site_inputs, realtime_parking_site_errors)

        for realtime_parking_site_error in realtime_parking_site_errors:
            self.logger.warning(LogMessageType.FAILED_REALTIME_PARKING_SITE_HANDLING, str(realtime_parking_site_error))

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_status = SourceStatus.ACTIVE
        self.source_repository.save_source(source)

    def get_upserted_source(self, source_uid: str) -> Source:
        if source_uid not in self.park_api_sources.converter_by_uid:
            raise UnknownSourceException(message=f'Source {source_uid} is not supported.')

        try:
            source = self.source_repository.fetch_source_by_uid(source_uid)
        except ObjectNotFoundException:
            source = Source()
            source.uid = source_uid

        source_info = self.park_api_sources.converter_by_uid[source_uid].source_info
        for key, value in source_info.to_dict().items():
            if key not in ['uid', 'has_realtime_data']:
                setattr(source, key, value)

        if source_info.has_realtime_data is True and source.realtime_status == SourceStatus.DISABLED:
            source.realtime_status = SourceStatus.PROVISIONED
        elif source_info.has_realtime_data is False and source.realtime_status != SourceStatus.DISABLED:
            source.realtime_status = SourceStatus.DISABLED

        self.source_repository.save_source(source)
        return source

    def handle_static_import_results(
        self,
        source: Source,
        static_parking_site_inputs: list[StaticParkingSiteInput],
        static_parking_site_errors: list[ImportParkingSiteException],
    ):
        existing_parking_site_ids = self.parking_site_repository.fetch_parking_sites_ids_by_source_id(source.id)
        for static_parking_site_input in static_parking_site_inputs:
            try:
                self._save_static_parking_site_input(source, static_parking_site_input, existing_parking_site_ids)
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

    def _save_static_parking_site_input(
        self,
        source: Source,
        static_parking_site_input: StaticParkingSiteInput,
        existing_parking_site_ids: list[int],
    ):
        try:
            parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=static_parking_site_input.uid,
            )
            # If the ParkingSite exists: remove it from existing parking site list
            if parking_site.id in existing_parking_site_ids:
                existing_parking_site_ids.remove(parking_site.id)
        except ObjectNotFoundException:
            parking_site = ParkingSite()
            parking_site.source_id = source.id
            parking_site.original_uid = static_parking_site_input.uid

        history_enabled: bool = self.config_helper.get('HISTORY_ENABLED', False)
        history_changed = False
        for key, value in static_parking_site_input.to_dict().items():
            if key in ['uid', 'external_identifiers', 'tags', 'group_uid']:
                continue
            if (
                history_enabled
                and ('capacity' in key or key == 'realtime_opening_status')
                and getattr(parking_site, key) != value
            ):
                history_changed = True
            setattr(parking_site, key, value)

        if static_parking_site_input.external_identifiers not in [None, UnsetValue]:
            external_identifiers: list[ExternalIdentifier] = []
            for i, external_identifier_input in enumerate(static_parking_site_input.external_identifiers):
                if len(static_parking_site_input.external_identifiers) < len(parking_site.external_identifiers):
                    external_identifier = parking_site.external_identifiers[i]
                else:
                    external_identifier = ExternalIdentifier()
                external_identifier.type = external_identifier_input.type
                external_identifier.value = external_identifier_input.value
                external_identifiers.append(external_identifier)
            parking_site.external_identifiers = external_identifiers

        if static_parking_site_input.tags not in [None, UnsetValue]:
            tags: list[Tag] = []
            for i, tag_input in enumerate(static_parking_site_input.tags):
                if len(static_parking_site_input.tags) < len(parking_site.tags):
                    tag = parking_site.tags[i]
                else:
                    tag = Tag()
                tag.value = tag_input
                tags.append(tag)
            parking_site.tags = tags

        if static_parking_site_input.group_uid:
            try:
                parking_site_group = self.parking_site_group_repository.fetch_parking_site_group_by_original_uid(
                    static_parking_site_input.group_uid,
                )
            except ObjectNotFoundException:
                parking_site_group = ParkingSiteGroup()
                parking_site_group.original_uid = static_parking_site_input.group_uid
                parking_site_group.source_id = parking_site.source_id

            parking_site.parking_site_group = parking_site_group
        else:
            parking_site.parking_site_group_id = None

        self.parking_site_repository.save_parking_site(parking_site)
        if history_enabled and history_changed:
            self._add_history(parking_site)

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
            if realtime_free_capacity is None or realtime_free_capacity is UnsetValue:
                continue

            realtime_capacity = getattr(realtime_parking_site_input, f'realtime_{capacity_field}')

            parking_site_capacity = getattr(parking_site, capacity_field)
            if parking_site_capacity is None:
                continue

            if realtime_capacity is UnsetValue or realtime_capacity is None:
                if realtime_free_capacity > parking_site_capacity:
                    setattr(realtime_parking_site_input, f'realtime_free_{capacity_field}', parking_site_capacity)
                    self.logger.warning(
                        LogMessageType.FAILED_PARKING_SITE_HANDLING,
                        f'At {parking_site.original_uid} from {source.id}, '
                        f'realtime_free_{capacity_field} {realtime_free_capacity} '
                        f'was higher than {capacity_field} {parking_site_capacity}',
                    )

            if realtime_capacity is not UnsetValue and realtime_capacity is not None:
                if realtime_free_capacity > realtime_capacity:
                    setattr(realtime_parking_site_input, f'realtime_free_{capacity_field}', realtime_capacity)
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
