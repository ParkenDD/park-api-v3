"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from webapp.models import ParkingSite, Source
from webapp.models.parking_site import OpeningStatus, ParkingSiteType
from webapp.models.source import SourceStatus
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException

if TYPE_CHECKING:
    from webapp.converter.common.models import ImportSourceResult
    from webapp.converter.common.validators import RealtimeParkingSiteInput, StaticParkingSiteInput


class HandleConverterImportResultMixin:
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository

    def _handle_import_results(self, source: Source, import_results: 'ImportSourceResult'):
        # set source data
        for key in ['name', 'public_url', 'attribution_license', 'attribution_contributor', 'attribution_url']:
            setattr(source, key, getattr(import_results, key, None))

        # static data
        if import_results.static_parking_site_inputs:
            for static_parking_site_input in import_results.static_parking_site_inputs:
                self._save_static_parking_site_input(source, static_parking_site_input)

            if len(import_results.static_parking_site_inputs):
                source.static_status = SourceStatus.ACTIVE
            elif import_results.static_parking_site_error_count:
                source.static_status = SourceStatus.FAILED

            source.static_data_updated_at = datetime.now(tz=timezone.utc)
            source.static_parking_site_error_count = import_results.static_parking_site_error_count

        # realtime data
        if import_results.realtime_parking_site_inputs and source.static_status == SourceStatus.ACTIVE:
            realtime_parking_site_error_count = import_results.realtime_parking_site_error_count or 0
            for realtime_parking_site_inputs in import_results.realtime_parking_site_inputs:
                try:
                    self._save_realtime_parking_site_input(source, realtime_parking_site_inputs)
                except ObjectNotFoundException:
                    realtime_parking_site_error_count += 1

            if len(import_results.realtime_parking_site_inputs):
                source.realtime_status = SourceStatus.ACTIVE
            elif import_results.realtime_parking_site_error_count:
                source.realtime_status = SourceStatus.FAILED

            source.realtime_status = SourceStatus.ACTIVE
            source.realtime_data_updated_at = datetime.now(tz=timezone.utc)
            source.realtime_parking_site_error_count = import_results.realtime_parking_site_error_count

        self.source_repository.save_source(source)

    def _save_static_parking_site_input(self, source: Source, static_parking_site_input: 'StaticParkingSiteInput'):
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

    def _save_realtime_parking_site_input(self, source: Source, realtime_parking_site_input: 'RealtimeParkingSiteInput'):
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
