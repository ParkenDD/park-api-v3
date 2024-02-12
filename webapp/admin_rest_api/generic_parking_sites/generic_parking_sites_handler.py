"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import BytesIO, StringIO
from typing import TYPE_CHECKING
from zipfile import BadZipFile

from lxml import etree
from lxml.etree import ParseError
from openpyxl.reader.excel import load_workbook

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.common.logging.models import LogTag
from webapp.common.rest.exceptions import InvalidInputException, RestApiNotImplementedException
from webapp.models import Source
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.import_service import ParkingSiteGenericImportService
from webapp.shared.source import HandleConverterImportResultMixin

if TYPE_CHECKING:
    from webapp.converter.common.models import ImportSourceResult


class GenericParkingSitesHandler(AdminApiBaseHandler, HandleConverterImportResultMixin):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository
    parking_site_generic_import_service: ParkingSiteGenericImportService

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
        parking_site_generic_import_service: ParkingSiteGenericImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository
        self.parking_site_generic_import_service = parking_site_generic_import_service

    def handle_json_data(self, source_uid: str, data: dict | list) -> 'ImportSourceResult':
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        import_results = import_service.handle_json(data)

        self._handle_import_results(source, import_results)

        return import_results

    def handle_xml_data(self, source_uid: str, data: bytes) -> 'ImportSourceResult':
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        try:
            root_element = etree.fromstring(data, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320
        except ParseError as e:
            raise InvalidInputException(message='Invalid XML file') from e

        import_results = import_service.handle_xml(root_element)

        self._handle_import_results(source, import_results)

        return import_results

    def handle_csv_data(self, source_uid: str, data: str) -> 'ImportSourceResult':
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        try:
            import_results = import_service.handle_csv_string(StringIO(data))
        except Exception as e:
            raise InvalidInputException(message=f'Invalid input: {getattr(e, "message", "unknown reason")}') from e

        self._handle_import_results(source, import_results)

        return import_results

    def handle_xlsx_data(self, source_uid: str, data: bytes) -> 'ImportSourceResult':
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        try:
            workbook = load_workbook(filename=BytesIO(data))
        # Sadly, there is no generic parent exception load_workbook throws, so this list might be incomplete
        except (BadZipFile, KeyError, ValueError) as e:
            raise InvalidInputException(message='Invalid XLSX file') from e

        try:
            import_results = import_service.handle_xlsx(workbook)
        except Exception as e:
            raise InvalidInputException(message=f'Invalid input: {getattr(e, "message", "unknown reason")}') from e

        self._handle_import_results(source, import_results)

        return import_results

    def _get_source(self, source_uid: str) -> Source:
        try:
            source = self.source_repository.fetch_source_by_uid(source_uid)
        except ObjectNotFoundException:
            source = Source()
            source.uid = source_uid
            self.source_repository.save_source(source)
        self.logger.set_tag(LogTag.SOURCE, source_uid)

        if source_uid not in self.parking_site_generic_import_service.push_converters:
            raise RestApiNotImplementedException(message='Converter is missing for this source.')

        return source
