"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from flask import Flask

from parkapi_sources import ParkAPISources
from parkapi_sources.converters.base_converter.parking_spot_base_converter import ParkingSpotBaseConverter
from parkapi_sources.converters.base_converter.pull import PullConverter
from webapp.common.logging.models import LogMessageType, LogTag
from webapp.common.rest.exceptions import UnknownSourceException
from webapp.models import Source
from webapp.models.source import SourceStatus
from webapp.repositories import SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService

from .generic_parking_site_import_service import GenericParkingSiteImportService
from .generic_parking_spot_import_service import GenericParkingSpotImportService


class GenericImportService(BaseService):
    source_repository: SourceRepository
    generic_parking_site_import_service: GenericParkingSiteImportService
    generic_parking_spot_import_service: GenericParkingSpotImportService

    park_api_sources: ParkAPISources

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        generic_parking_site_import_service: GenericParkingSiteImportService,
        generic_parking_spot_import_service: GenericParkingSpotImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.generic_parking_site_import_service = generic_parking_site_import_service
        self.generic_parking_spot_import_service = generic_parking_spot_import_service

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
            custom_converters=app.config.get('PARK_API_SOURCES_CUSTOM_CONVERTERS'),
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

        if hasattr(converter, 'get_static_parking_sites'):
            try:
                static_parking_site_inputs, static_parking_site_errors = converter.get_static_parking_sites()
            except Exception as e:
                self.logger.warning(message_type=LogMessageType.FAILED_STATIC_SOURCE_HANDLING, message=str(e))
                source.static_status = SourceStatus.FAILED
                self.source_repository.save_source(source)
                return

            self.generic_parking_site_import_service.handle_static_import_results(
                source, static_parking_site_inputs, static_parking_site_errors
            )

            for static_parking_site_error in static_parking_site_errors:
                self.logger.warning(LogMessageType.FAILED_STATIC_PARKING_SITE_HANDLING, str(static_parking_site_error))

        if isinstance(converter, ParkingSpotBaseConverter):
            try:
                static_parking_spot_inputs, static_parking_spot_errors = converter.get_static_parking_spots()
            except Exception as e:
                self.logger.warning(message_type=LogMessageType.FAILED_STATIC_SOURCE_HANDLING, message=str(e))
                source.static_status = SourceStatus.FAILED
                self.source_repository.save_source(source)
                return

            self.generic_parking_spot_import_service.handle_static_import_results(
                source, static_parking_spot_inputs, static_parking_spot_errors
            )

            for static_parking_spot_error in static_parking_spot_errors:
                self.logger.warning(LogMessageType.FAILED_STATIC_PARKING_SPOT_HANDLING, str(static_parking_spot_error))

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

        if hasattr('converter', 'get_realtime_parking_sites'):
            try:
                realtime_parking_site_inputs, realtime_parking_site_errors = converter.get_realtime_parking_sites()
            except Exception as e:
                self.logger.warning(message_type=LogMessageType.FAILED_REALTIME_SOURCE_HANDLING, message=str(e))
                source.realtime_status = SourceStatus.FAILED
                self.source_repository.save_source(source)
                return

            self.generic_parking_site_import_service.handle_realtime_import_results(
                source, realtime_parking_site_inputs, realtime_parking_site_errors
            )

            for realtime_parking_site_error in realtime_parking_site_errors:
                self.logger.warning(
                    LogMessageType.FAILED_REALTIME_PARKING_SITE_HANDLING, str(realtime_parking_site_error)
                )

        if isinstance(converter, ParkingSpotBaseConverter):
            try:
                realtime_parking_spot_inputs, realtime_parking_spot_errors = converter.get_realtime_parking_spots()
            except Exception as e:
                self.logger.warning(message_type=LogMessageType.FAILED_REALTIME_SOURCE_HANDLING, message=str(e))
                source.realtime_status = SourceStatus.FAILED
                self.source_repository.save_source(source)
                return

            self.generic_parking_spot_import_service.handle_realtime_import_results(
                source, realtime_parking_spot_inputs, realtime_parking_spot_errors
            )

            for realtime_parking_spot_error in realtime_parking_spot_errors:
                self.logger.warning(
                    LogMessageType.FAILED_REALTIME_PARKING_SPOT_HANDLING, str(realtime_parking_spot_error)
                )

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
