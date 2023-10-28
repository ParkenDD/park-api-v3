"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from io import BytesIO, StringIO

from lxml import etree
from openpyxl.reader.excel import load_workbook

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.common.rest.exceptions import RestApiNotImplementedException
from webapp.models import ParkingSite, Source
from webapp.models.parking_site import ParkingSiteType
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.import_service import ParkingSiteGenericImportService


class GenericParkingSitesHandler(AdminApiBaseHandler):
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

    def handle_json_data(self, source_uid: str, data: dict | list):
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        import_results = import_service.handle_json(data)
        static_parking_site_inputs = import_results.static_parking_site_inputs

        for static_parking_site_input in static_parking_site_inputs:
            self._save_parking_site_input(source, static_parking_site_input)

    def handle_xml_data(self, source_uid: str, data: str):
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        root_element = etree.parse(StringIO(data), parser=etree.XMLParser(resolve_entities=False))  # noqa: S320
        import_results = import_service.handle_xml(root_element)
        static_parking_site_inputs = import_results.static_parking_site_inputs

        for static_parking_site_input in static_parking_site_inputs:
            self._save_parking_site_input(source, static_parking_site_input)

    def handle_csv_data(self, source_uid: str, data: str):
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        rows = list(csv.reader(StringIO(data)))
        import_results = import_service.handle_csv(rows)
        static_parking_site_inputs = import_results.static_parking_site_inputs

        for static_parking_site_input in static_parking_site_inputs:
            self._save_parking_site_input(source, static_parking_site_input)

    def handle_xlsx_data(self, source_uid: str, data: bytes):
        source = self._get_source(source_uid)
        import_service = self.parking_site_generic_import_service.push_converters[source_uid]

        workbook = load_workbook(filename=BytesIO(data))
        import_results = import_service.handle_xlsx(workbook)
        static_parking_site_inputs = import_results.static_parking_site_inputs

        for static_parking_site_input in static_parking_site_inputs:
            self._save_parking_site_input(source, static_parking_site_input)

    def _get_source(self, source_uid: str) -> Source:
        try:
            source = self.source_repository.fetch_source_by_uid(source_uid)
        except ObjectNotFoundException:
            source = Source()
            source.uid = source_uid
            self.source_repository.save_source(source)

        if source_uid not in self.parking_site_generic_import_service.push_converters:
            raise RestApiNotImplementedException(message='Converter is missing for this source.')

        return source

    def _save_parking_site_input(self, source: Source, static_parking_site_input):
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
            if key in ['uid']:
                continue
            if key == 'type' and value:
                value = ParkingSiteType[value.name]
            setattr(parking_site, key, value)

        self.parking_site_repository.save_parking_site(parking_site)
