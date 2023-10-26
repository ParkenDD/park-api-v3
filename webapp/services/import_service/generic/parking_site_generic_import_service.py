"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import sys
from datetime import datetime, timezone
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

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
from .parking_site_generic_import_mapper import ParkingSiteGenericImportMapper
from .parking_site_generic_import_validator import LotDataInput, LotInfoInput


class ParkingSiteGenericImportService(BaseService):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository

    converters: dict[str, ]

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

        self.converters = {}
        self.register_converters()

    def register_converters(self):
        # the following code is a converter autoloader. It dynamically adds all converters in ./converters.
        base_package_dir = Path(self.config_helper.get('PROJECT_ROOT')).resolve().joinpath('converter')
        # appending the base package dir gives converters the ability to work within their own module without relative paths
        sys.path.append(str(base_package_dir))
        # This import is based on the additional module path just added to sys
        from util import ScraperBase

        for source_dir in ['original', 'new']:
            package_dir = base_package_dir.joinpath(source_dir)
            for _, module_name, _ in iter_modules([str(package_dir)]):
                # load all modules in converters
                module = import_module(f'{source_dir}.{module_name}')
                # look for attributes
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if not isclass(attribute):
                        continue
                    if not issubclass(attribute, ScraperBase) or attribute is ScraperBase:
                        continue
                    # at this point we can be sure that attribute is a ScraperBase child, so we can initialize and register it
                    self.converters[attribute.POOL.id] = attribute()

    def update_sources_static(self):
        for source in self.config_helper.get('PARK_API_CONVERTER'):
            try:
                self.update_source_static(source)
            except ConverterMissingException:
                self.logger.info('converter', f'ignored source {source} because converter is missing')
                continue

    def update_source_static(self, source_uid: str):
        if source_uid not in self.converters:
            raise ConverterMissingException(f'converter {source_uid} is missing')

        try:
            source = self.source_repository.fetch_source_by_uid(source_uid)
        except ObjectNotFoundException:
            source = self.create_source(source_uid)

        try:
            lot_infos = self.converters[source_uid].get_lot_infos()
        except Exception:
            source.status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        if getattr(lot_infos, 'lot_error_count', None) is not None:
            source.realtime_parking_site_error_count = getattr(lot_infos, 'lot_error_count')

        for lot_info in lot_infos:
            try:
                self.update_parking_site_static(source, lot_info)
            except ImportDatasetException as e:
                self.logger.info(
                    'generic-import',
                    f'source {source.id} {source.uid} dataset {e.dataset} failed to import because of {e.exception.code}',
                )

        source.static_data_updated_at = datetime.now(tz=timezone.utc)
        source.status = SourceStatus.ACTIVE
        self.source_repository.save_source(source)

    def update_parking_site_static(self, source: Source, lot_info: LotInfo):
        try:
            lot_info_input = self.lot_info_validator.validate(lot_info.to_dict())
        except ValidationError as e:
            raise ImportDatasetException(dataset=lot_info.to_dict(), exception=e) from e
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

    def create_source(self, source_uid: str) -> Source:
        source = Source()
        source.uid = source_uid
        park_api_pool = self.converters[source_uid].POOL
        for key in [
            'public_url',
            'attribution_license',
            'attribution_url',
            'attribution_contributor',
        ]:
            setattr(source, key, getattr(park_api_pool, key))
        self.source_repository.save_source(source)
        return source

    def update_source_realtime(self, source_uid: str):
        if source_uid not in self.converters:
            raise ConverterMissingException(f'converter {source_uid} is missing')

        source = self.source_repository.fetch_source_by_uid(source_uid)

        if source.status == SourceStatus.FAILED:
            return

        try:
            lot_datasets = self.converters[source_uid].get_lot_data()
        except Exception:
            source.status = SourceStatus.FAILED
            self.source_repository.save_source(source)
            return

        if getattr(lot_datasets, 'lot_error_count', None) is not None:
            source.realtime_parking_site_error_count = getattr(lot_datasets, 'lot_error_count')

        for lot_data in lot_datasets:
            try:
                self.update_parking_site_realtime(source, lot_data)
            except ImportDatasetException as e:
                self.logger.info(
                    'generic-import',
                    f'source {source.id} {source.uid} dataset {e.dataset} failed to import because of {e.exception.message}',
                )
        source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
        self.source_repository.save_source(source)

    def update_parking_site_realtime(self, source: Source, lot_info: LotData):
        try:
            lot_data_input = self.lot_data_validator.validate(lot_info.to_dict())
        except ValidationError as e:
            raise ImportDatasetException(dataset=lot_info.to_dict(), exception=e) from e

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
