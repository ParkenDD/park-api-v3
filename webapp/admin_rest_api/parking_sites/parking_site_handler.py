"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from json import JSONDecodeError
from pathlib import Path

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import CombinedParkingSiteInput, StaticParkingSitePatchInput, StaticPatchInput
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator
from validataclass_search_queries.pagination import PaginatedResult

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.admin_rest_api.parking_sites.parking_site_response import ParkingSiteResponse
from webapp.admin_rest_api.parking_sites.parking_site_validators import ApplyDuplicatesInput, GetDuplicatesInput
from webapp.models import ParkingSite
from webapp.repositories import ParkingSiteRepository, SourceRepository
from webapp.services.import_service.generic import GenericParkingSiteImportService
from webapp.services.matching_service import DuplicatedParkingSite, MatchingService
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteBaseSearchInput, ParkingSiteGeoSearchInput


class ParkingSiteHandler(AdminApiBaseHandler):
    parking_site_repository: ParkingSiteRepository
    source_repository: SourceRepository
    matching_service: MatchingService
    generic_parking_site_import_service: GenericParkingSiteImportService

    combined_parking_site_validator = DataclassValidator(CombinedParkingSiteInput)
    static_patch_input_validator = DataclassValidator(StaticPatchInput)
    static_parking_site_patch_validator = DataclassValidator(StaticParkingSitePatchInput)

    def __init__(
        self,
        *args,
        parking_site_repository: ParkingSiteRepository,
        matching_service: MatchingService,
        source_repository: SourceRepository,
        generic_parking_site_import_service: GenericParkingSiteImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.source_repository = source_repository
        self.matching_service = matching_service
        self.generic_parking_site_import_service = generic_parking_site_import_service

    def get_parking_sites(self, search_query: ParkingSiteGeoSearchInput) -> PaginatedResult[ParkingSite]:
        return self.parking_site_repository.fetch_parking_sites(search_query=search_query)

    def get_parking_site(self, parking_site_id: int) -> ParkingSite:
        return self.parking_site_repository.fetch_parking_site_by_id(parking_site_id)

    def upsert_parking_site_list(self, source_uid: str, parking_site_dicts: list[dict]) -> ParkingSiteResponse:
        response = ParkingSiteResponse()
        source = self.source_repository.fetch_source_by_uid(source_uid)
        parking_site_ids = self.parking_site_repository.fetch_parking_site_ids_by_source_id(source_id=source.id)

        combined_parking_site_inputs: list[CombinedParkingSiteInput] = []

        for parking_site_dict in parking_site_dicts:
            try:
                combined_parking_site_input = self.combined_parking_site_validator.validate(parking_site_dict)
            except ValidationError as e:
                response.errors.append(
                    ImportParkingSiteException(
                        source_uid=source_uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        data=e.to_dict(),
                        message='Invalid parking site',
                    ),
                )
                continue
            combined_parking_site_inputs.append(combined_parking_site_input)

        combined_parking_site_inputs = self.apply_static_patches(
            source_uid=source.uid,
            parking_site_inputs=combined_parking_site_inputs,
        )

        for combined_parking_site_input in combined_parking_site_inputs:
            parking_site = self.generic_parking_site_import_service.save_static_or_combined_parking_site_input(
                source=source,
                parking_site_input=combined_parking_site_input,
                existing_parking_site_ids=parking_site_ids,
            )

            response.items.append(self._map_parking_site(parking_site))

        return response

    def upsert_parking_site_item(
        self,
        source_uid: str,
        combined_parking_site_input: CombinedParkingSiteInput,
    ) -> dict:
        source = self.source_repository.fetch_source_by_uid(source_uid)

        (combined_parking_site_input,) = self.apply_static_patches(
            source_uid=source.uid,
            parking_site_inputs=[combined_parking_site_input],
        )

        parking_site = self.generic_parking_site_import_service.save_static_or_combined_parking_site_input(
            source=source,
            parking_site_input=combined_parking_site_input,
            existing_parking_site_ids=[],
        )

        return self._map_parking_site(parking_site)

    def generate_duplicates(self, duplicate_input: GetDuplicatesInput) -> list[DuplicatedParkingSite]:
        duplicate_ids: list[tuple[int, int]] = [
            (duplicate[0], duplicate[1]) for duplicate in duplicate_input.old_duplicates
        ]
        if duplicate_input.source_ids is not None:
            source_ids = duplicate_input.source_ids
        elif duplicate_input.source_uids is not None:
            source_ids = self.source_repository.fetch_source_ids_by_source_uids(duplicate_input.source_uids)
        else:
            source_ids = None

        return self.matching_service.generate_duplicates(
            duplicate_ids,
            match_radius=duplicate_input.radius,
            source_ids=source_ids,
        )

    def apply_duplicates(self, apply_duplicate_input: ApplyDuplicatesInput) -> list[DuplicatedParkingSite]:
        return self.matching_service.apply_duplicates(apply_duplicate_input.keep, apply_duplicate_input.ignore)

    @staticmethod
    def _map_parking_site(parking_site: ParkingSite) -> dict:
        return parking_site.to_dict(
            include_external_identifiers=True,
            include_tags=True,
            include_group=True,
        )

    def apply_static_patches(
        self,
        source_uid: str,
        parking_site_inputs: list[CombinedParkingSiteInput],
    ) -> list[CombinedParkingSiteInput]:
        if not self.config_helper.get('PARKING_SITE_PATCH_DIR'):
            return parking_site_inputs

        json_file_path = Path(self.config_helper.get('PARKING_SITE_PATCH_DIR'), f'{source_uid}.json')

        if not json_file_path.exists():
            return parking_site_inputs

        with json_file_path.open() as json_file:
            try:
                item_dicts = json.loads(json_file.read())
            except JSONDecodeError:
                return parking_site_inputs

        parking_site_inputs_by_uid: dict[str, CombinedParkingSiteInput] = {
            parking_site_input.uid: parking_site_input for parking_site_input in parking_site_inputs
        }

        try:
            items = self.static_patch_input_validator.validate(item_dicts)
        except ValidationError:
            return parking_site_inputs

        for item_dict in items.items:
            try:
                parking_site_patch = self.static_parking_site_patch_validator.validate(item_dict)
            except ValidationError:
                continue

            if parking_site_patch.uid not in parking_site_inputs_by_uid:
                continue

            for key, value in parking_site_patch.to_dict().items():
                setattr(parking_site_inputs_by_uid[parking_site_patch.uid], key, value)

        return parking_site_inputs

    def reset_duplicates(self, search_query: ParkingSiteBaseSearchInput):
        return self.matching_service.reset_matching(search_query)
