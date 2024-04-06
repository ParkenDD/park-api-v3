"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from flask import Flask
from parkapi_sources import ParkAPISources
from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkingSiteType

from webapp.common.logging.models import LogMessageType, LogTag
from webapp.models import ExternalIdentifier, ParkingSite, Source
from webapp.models.source import SourceStatus
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService


class ParkingSiteGenericImportService(BaseService):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository
    park_api_sources: ParkAPISources

    def __init__(self, *args, source_repository: SourceRepository, parking_site_repository: ParkingSiteRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository

    def init_app(self, app: Flask):
        park_api_source_uids: list[str] = []
        park_api_sources_config: dict[str, str] = {}
        for source_dict in app.config.get('PARK_API_CONVERTER', {}):
            park_api_source_uids.append(source_dict['uid'])
            if 'env' in source_dict:
                park_api_sources_config.update(source_dict['env'])
        self.park_api_sources = ParkAPISources(converter_uids=park_api_source_uids, config=park_api_sources_config)
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
            self.logger.info(message_type=LogMessageType.FAILED_SOURCE_HANDLING, message=str(e))
            source.static_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        self.handle_static_import_results(source, static_parking_site_inputs, static_parking_site_errors)

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
            self.logger.info(message_type=LogMessageType.FAILED_SOURCE_HANDLING, message=str(e))
            source.realtime_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        self.handle_realtime_import_results(source, realtime_parking_site_inputs, realtime_parking_site_errors)

        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        source.realtime_status = SourceStatus.ACTIVE
        self.source_repository.save_source(source)

    def get_upserted_source(self, source_uid: str) -> Source:
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
        for static_parking_site_input in static_parking_site_inputs:
            self._save_static_parking_site_input(source, static_parking_site_input)

        if len(static_parking_site_inputs):
            source.static_status = SourceStatus.ACTIVE
        elif len(static_parking_site_errors):
            source.realtime_status = SourceStatus.FAILED

        source.static_data_updated_at = datetime.now(tz=timezone.utc)
        source.static_parking_site_error_count = len(static_parking_site_errors)

    def _save_static_parking_site_input(self, source: Source, static_parking_site_input: StaticParkingSiteInput):
        try:
            parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=static_parking_site_input.uid,
            )
        except ObjectNotFoundException:
            parking_site = ParkingSite()
            parking_site.source_id = source.id
            parking_site.original_uid = static_parking_site_input.uid

        for key, value in static_parking_site_input.to_dict().items():
            if key in ['uid', 'external_identifiers']:
                continue
            if key == 'type' and value:
                value = ParkingSiteType[value.name]
            setattr(parking_site, key, value)

        if static_parking_site_input.external_identifiers:
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

        self.parking_site_repository.save_parking_site(parking_site)

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

        for key, value in realtime_parking_site_input.to_dict().items():
            if key in ['uid']:
                continue
            if key == 'realtime_opening_status' and value:
                value = OpeningStatus[value.name]
            setattr(parking_site, key, value)

        self.parking_site_repository.save_parking_site(parking_site)
