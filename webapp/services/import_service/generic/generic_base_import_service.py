"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources import ParkAPISources
from parkapi_sources.models import StaticBaseParkingInput

from webapp.models import ExternalIdentifier, ParkingRestriction, ParkingSite, ParkingSpot, Tag
from webapp.repositories import SourceRepository
from webapp.services.base_service import BaseService


class GenericBaseImportService(BaseService):
    source_repository: SourceRepository
    park_api_sources: ParkAPISources

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository

    @staticmethod
    def set_related_objects(entity_input: StaticBaseParkingInput, entity: ParkingSite | ParkingSpot):
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
