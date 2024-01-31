"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import sys
import traceback
from datetime import datetime, timezone
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules
from typing import TYPE_CHECKING

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from webapp.common.error_handling.exceptions import AppException
from webapp.common.logging.models import LogMessageType, LogTag
from webapp.converter.util import LotData, LotInfo
from webapp.models import ParkingSite, Source
from webapp.models.source import SourceStatus
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService
from webapp.services.import_service.exceptions import (
    ConverterMissingException,
    ImportDatasetException,
)
from webapp.shared.source import HandleConverterImportResultMixin

from .parking_site_generic_import_mapper import ParkingSiteGenericImportMapper
from .parking_site_generic_import_validator import LotDataInput, LotInfoInput

if TYPE_CHECKING:
    from webapp.converter.common.models import ImportSourceResult
    from webapp.converter.util import LotDataList, LotInfoList


class SourceFailedException(AppException):
    pass


class ParkingSiteGenericImportService(BaseService, HandleConverterImportResultMixin):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository

    pull_converters: dict
    push_converters: dict

    lot_info_validator = DataclassValidator(LotInfoInput)
    lot_data_validator = DataclassValidator(LotDataInput)

    import_mapper = ParkingSiteGenericImportMapper()

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository

        self.pull_converters = {}
        self.legacy_pull_converters = {}
        self.push_converters = {}
        self.register_converters()

    def register_converters(self):
        # the following code is a converter autoloader. It dynamically adds all converters in ./converters.
        base_package_dir = Path(self.config_helper.get('PROJECT_ROOT')).resolve().joinpath('converter')
        # appending the base package dir gives converters the ability to work within their own module without relative paths
        sys.path.append(str(base_package_dir))
        # This import is based on the additional module path just added to sys
        from common.base_converter import PullConverter
        from util import ScraperBase, SourceInfo

        for source_dir in ['original', 'new', 'v3']:
            package_dir = base_package_dir.joinpath(source_dir)
            for _, module_name, _ in iter_modules([str(package_dir)]):
                # load all modules in converters
                module = import_module(f'{source_dir}.{module_name}')
                # look for attributes
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if not isclass(attribute):
                        continue
                    if source_dir in ['original', 'new']:
                        if not issubclass(attribute, ScraperBase) or attribute is ScraperBase:
                            continue
                        # at this point we can be sure that attribute is a ScraperBase child, so we can initialize and register it
                        self.legacy_pull_converters[attribute.POOL.id] = attribute()
                        continue

                    # source_info is just set at actual final classes, so we ignore anything else
                    if not hasattr(attribute, 'source_info') or not isinstance(attribute.source_info, SourceInfo):
                        continue

                    # at this point we can be sure that attribute is a BaseConverter or PullConverter child, so we can initialize and
                    # register it
                    if issubclass(attribute, PullConverter):
                        self.pull_converters[attribute.source_info.id] = attribute()
                    else:
                        self.push_converters[attribute.source_info.id] = attribute()

    def update_sources_static(self):
        for source in self.config_helper.get('PARK_API_CONVERTER'):
            try:
                self.update_source_static(source)
            except ConverterMissingException:
                self.logger.info(LogMessageType.MISC, f'ignored source {source} because converter is missing')
                continue

    def update_source_static(self, source_uid: str):
        self.logger.set_tag(LogTag.SOURCE, source_uid)

        if source_uid not in self.pull_converters and source_uid not in self.legacy_pull_converters:
            raise ConverterMissingException(f'converter {source_uid} is missing')

        try:
            source = self.source_repository.fetch_source_by_uid(source_uid)
        except ObjectNotFoundException:
            source = self._create_source(source_uid)

        try:
            if source_uid in self.legacy_pull_converters:
                self._update_legacy_source_static(source)
            else:
                self._update_source_static(source)

            source.static_data_updated_at = datetime.now(tz=timezone.utc)
            source.static_status = SourceStatus.ACTIVE
            self.source_repository.save_source(source)

        except SourceFailedException as e:
            self.logger.info(message_type=LogMessageType.FAILED_SOURCE_HANDLING, message=e.message)
            source.static_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

    def _update_source_static(self, source: Source):
        try:
            import_source_result: 'ImportSourceResult' = self.pull_converters[source.uid].get_static_parking_sites()
        except Exception as e:
            raise SourceFailedException(
                message=f'handling static source {source.uid} failed: {repr(e)}:\n{traceback.format_exc().splitlines()}'
            ) from e
        self._handle_import_results(source, import_source_result)

    def _update_legacy_source_static(self, source: Source):
        try:
            lot_infos: LotInfoList | list = self.legacy_pull_converters[source.uid].get_lot_infos()
        except Exception as e:
            raise SourceFailedException(
                message=f'handling static source {source.uid} failed: {repr(e)}:\n{traceback.format_exc().splitlines()}'
            ) from e

        if len(lot_infos) == 0:
            raise SourceFailedException(message=f'handling static source {source.uid} has no entries')

        if getattr(lot_infos, 'errors', None) is not None:
            for error in lot_infos.errors:
                self.logger.info(
                    LogMessageType.FAILED_PARKING_SITE_HANDLING,
                    f'source {source.id} {source.uid} static dataset failed: {error}',
                )
            source.static_parking_site_error_count = lot_infos.error_count or 0
        else:
            source.static_parking_site_error_count = 0

        for lot_info in lot_infos:
            try:
                self._legacy_update_parking_site_static(source, lot_info)
            except ImportDatasetException as e:
                self.logger.info(
                    LogMessageType.FAILED_PARKING_SITE_HANDLING,
                    f'source {source.id} {source.uid} static dataset {e.dataset} failed to import because of {e.exception.code}: '
                    f'{e.exception_message}',
                )
                source.static_parking_site_error_count += 1

    def _legacy_update_parking_site_static(self, source: Source, lot_info: LotInfo):
        try:
            lot_info_input = self.lot_info_validator.validate(lot_info.to_dict())
        except ValidationError as e:
            raise ImportDatasetException(dataset=lot_info.to_dict(), exception=e) from e

        self.logger.set_tag(LogTag.PARKING_SITE, lot_info_input.id)

        try:
            parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=lot_info_input.id,
            )
        except ObjectNotFoundException:
            parking_site = ParkingSite()
            parking_site.source_id = source.id
            parking_site.original_uid = lot_info_input.id

        parking_site.static_data_updated_at = datetime.now(tz=timezone.utc)
        self.import_mapper.map_lot_info_to_parking_site(lot_info_input, parking_site)
        self.parking_site_repository.save_parking_site(parking_site)

    def _create_source(self, source_uid: str) -> Source:
        source = Source()
        source.uid = source_uid
        if source_uid in self.legacy_pull_converters:
            source_info = self.legacy_pull_converters[source_uid].POOL
        else:
            source_info = self.pull_converters[source_uid].source_info
        for key in [
            'public_url',
            'attribution_license',
            'attribution_url',
            'attribution_contributor',
        ]:
            setattr(source, key, getattr(source_info, key))
        self.source_repository.save_source(source)
        return source

    def update_sources_realtime(self):
        for source in self.config_helper.get('PARK_API_CONVERTER'):
            try:
                self.update_source_realtime(source)
            except ConverterMissingException:
                self.logger.info(LogMessageType.MISC, f'ignored source {source} because converter is missing')
                continue

    def update_source_realtime(self, source_uid: str):
        self.logger.set_tag(LogTag.SOURCE, source_uid)

        if source_uid not in self.pull_converters and source_uid not in self.legacy_pull_converters:
            raise ConverterMissingException(f'converter {source_uid} is missing')

        source = self.source_repository.fetch_source_by_uid(source_uid)

        # We can't do realtime updates when static data is not active
        if source.static_status != SourceStatus.ACTIVE:
            return

        # We don't do realtime updates if it's disabled
        if source.realtime_status == SourceStatus.DISABLED:
            return

        try:
            if source_uid in self.legacy_pull_converters:
                self._update_legacy_source_realtime(source)
            else:
                self._update_source_realtime(source)

            source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
            source.realtime_status = SourceStatus.ACTIVE
            self.source_repository.save_source(source)

        except SourceFailedException as e:
            self.logger.info(message_type=LogMessageType.FAILED_SOURCE_HANDLING, message=e.message)
            source.realtime_status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

    def _update_source_realtime(self, source: Source):
        try:
            import_source_result: 'ImportSourceResult' = self.pull_converters[source.uid].get_realtime_parking_sites()
        except Exception as e:
            raise SourceFailedException(
                message=f'handling realtime source {source.uid} failed: {repr(e)}:\n{traceback.format_exc().splitlines()}'
            ) from e
        self._handle_import_results(source, import_source_result)

    def _update_legacy_source_realtime(self, source: Source):
        try:
            lot_datasets: LotDataList | list = self.legacy_pull_converters[source.uid].get_lot_data()
        except Exception as e:
            raise SourceFailedException(
                message=f'handling realtime source {source.uid} failed: {repr(e)}:\n{traceback.format_exc().splitlines()}',
            ) from e

        if getattr(lot_datasets, 'error', None) is not None:
            for error in lot_datasets.errors:
                self.logger.info(
                    LogMessageType.FAILED_PARKING_SITE_HANDLING,
                    f'source {source.id} {source.uid} realtime dataset failed: {error}',
                )
            source.realtime_parking_site_error_count = lot_datasets.error_count or 0
        else:
            source.realtime_parking_site_error_count = 0

        for lot_data in lot_datasets:
            try:
                self.update_parking_site_realtime(source, lot_data)
            except ImportDatasetException as e:
                self.logger.info(
                    LogMessageType.MISC,
                    f'source {source.id} {source.uid} realtime dataset {e.dataset} failed to import because of {e.exception.code}: '
                    f'{e.exception_message}',
                )
                source.realtime_parking_site_error_count += 1

    def update_parking_site_realtime(self, source: Source, lot_info: LotData):
        try:
            lot_data_input = self.lot_data_validator.validate(lot_info.to_dict())
        except ValidationError as e:
            raise ImportDatasetException(dataset=lot_info.to_dict(), exception=e) from e

        self.logger.set_tag(LogTag.PARKING_SITE, lot_data_input.id)

        try:
            parking_site = self.parking_site_repository.fetch_parking_site_by_source_id_and_external_uid(
                source_id=source.id,
                original_uid=lot_data_input.id,
            )
        except ObjectNotFoundException as e:
            raise ImportDatasetException(dataset=lot_info.to_dict(), exception=e) from e

        self.import_mapper.map_lot_data_to_parking_site(lot_data_input, parking_site)
        parking_site.realtime_data_updated_at = lot_info.timestamp.replace(tzinfo=timezone.utc)

        self.parking_site_repository.save_parking_site(parking_site)
