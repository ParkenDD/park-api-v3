"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import structlog
from parkapi_sources import ParkAPISources
from parkapi_sources.models import StaticBaseParkingInput, StaticParkingSpotInput

from webapp.common.logging.models import LogMessageType
from webapp.models import ExternalIdentifier, ParkingRestriction, ParkingSite, ParkingSpot, Tag
from webapp.repositories import OfficialRegionCodeRepository, SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException
from webapp.services.base_service import BaseService

logger = structlog.get_logger(__name__)


class GenericBaseImportService(BaseService):
    source_repository: SourceRepository
    official_region_code_repository: OfficialRegionCodeRepository
    park_api_sources: ParkAPISources

    # Cached list of countries for which an official region code database is available. Empty until a database is found,
    # so it keeps re-checking until the regionalschluessel table has been imported.
    _official_region_code_databases: list[str] | None = None

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        official_region_code_repository: OfficialRegionCodeRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.official_region_code_repository = official_region_code_repository

    def assign_official_region_code(self, entity: ParkingSite | ParkingSpot) -> None:
        """
        Assigns the official region code (German Regionalschlüssel) based on the entity's coordinates, the same way the
        OCPDB does it with its Location model. Only assigns when not already set, if coordinates are available and if a
        region code database is available.
        """
        if entity.official_region_code or entity.lat is None or entity.lon is None:
            return

        # So far, only the German Regionalschlüssel is supported. As ParkAPI does not store a country, we assume DEU.
        if 'DEU' not in self._get_official_region_code_databases():
            return

        try:
            entity.official_region_code = (
                self.official_region_code_repository.fetch_official_region_code_by_coordinates(
                    country='DEU',
                    lat=entity.lat,
                    lon=entity.lon,
                )
            )
        except ObjectNotFoundException:
            logger.warning(
                f'Cannot find official regional code for coordinates {entity.lat} / {entity.lon}',
                type=LogMessageType.SOURCE_HANDLING,
            )

    def _get_official_region_code_databases(self) -> list[str]:
        if not self._official_region_code_databases:
            self._official_region_code_databases = self.official_region_code_repository.available_databases_by_country()
        return self._official_region_code_databases

    @staticmethod
    def set_related_objects(
        entity_input: StaticBaseParkingInput | StaticParkingSpotInput,
        entity: ParkingSite | ParkingSpot,
    ):
        if entity_input.restrictions is not None:
            parking_restrictions: list[ParkingRestriction] = []
            for i, parking_restrictions_input in enumerate(entity_input.restrictions):
                if len(entity_input.restrictions) <= len(entity.restrictions):
                    parking_restriction = entity.restrictions[i]
                else:
                    parking_restriction = ParkingRestriction()

                parking_restriction.from_dict(parking_restrictions_input.to_dict())

                parking_restrictions.append(parking_restriction)
            entity.restrictions = parking_restrictions
        else:
            entity.restrictions = []

        if entity_input.external_identifiers is not None:
            external_identifiers: list[ExternalIdentifier] = []
            for i, external_identifier_input in enumerate(entity_input.external_identifiers):
                if len(entity_input.external_identifiers) <= len(entity.external_identifiers):
                    external_identifier = entity.external_identifiers[i]
                else:
                    external_identifier = ExternalIdentifier()
                external_identifier.type = external_identifier_input.type
                external_identifier.value = external_identifier_input.value
                external_identifiers.append(external_identifier)
            entity.external_identifiers = external_identifiers

        if entity_input.tags is not None:
            tags: list[Tag] = []
            for i, tag_input in enumerate(entity_input.tags):
                if len(entity_input.tags) <= len(entity.tags):
                    tag = entity.tags[i]
                else:
                    tag = Tag()
                tag.value = tag_input
                tags.append(tag)
            entity.tags = tags
