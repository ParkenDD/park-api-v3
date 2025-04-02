"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Query, joinedload, selectinload
from validataclass_search_queries.filters import BoundSearchFilter
from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models import ParkingSpot, Source
from webapp.repositories import BaseRepository


class ParkingSpotRepository(BaseRepository[ParkingSpot]):
    model_cls = ParkingSpot

    def fetch_parking_spots(
        self,
        *,
        search_query: Optional[BaseSearchQuery] = None,
        include_source: bool = True,
        include_parking_restrictions: bool = False,
    ) -> PaginatedResult[ParkingSpot]:
        query = self.session.query(ParkingSpot)

        if include_source:
            query = query.options(joinedload(ParkingSpot.source))
        if include_parking_restrictions:
            query = query.options(selectinload(ParkingSpot.restricted_to))

        return self._search_and_paginate(query, search_query)

    def fetch_parking_spot_ids_by_source_id(self, source_id: int) -> list[int]:
        return self.session.scalars(select(ParkingSpot.id).where(ParkingSpot.source_id == source_id)).all()

    def fetch_parking_spot_by_id(self, parking_spot_id: int) -> ParkingSpot:
        return self.fetch_resource_by_id(parking_spot_id)

    def fetch_parking_spot_by_source_id_and_external_uid(self, source_id: int, original_uid: str) -> ParkingSpot:
        parking_spot: ParkingSpot | None = (
            self.session.query(ParkingSpot)
            .filter(ParkingSpot.source_id == source_id)
            .filter(ParkingSpot.original_uid == original_uid)
            .first()
        )

        return self._or_raise(
            parking_spot,
            f'ParkingSpot with source id {source_id} and original_uid {original_uid} not found',
        )

    def save_parking_spot(self, parking_spot: ParkingSpot, *, commit: bool = True):
        self._save_resources(parking_spot, commit=commit)

    def delete_parking_spot(self, parking_spot: ParkingSpot, *, commit: bool = True):
        self._delete_resources(parking_spot, commit=commit)

    def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
        if bound_filter.param_name == 'source_uid':
            return query.join(Source, Source.id == ParkingSpot.source_id).filter(Source.uid == bound_filter.value)
        if bound_filter.param_name == 'source_uids':
            return query.join(Source, Source.id == ParkingSpot.source_id).filter(Source.uid.in_(bound_filter.value))
        return super()._apply_bound_search_filter(query, bound_filter)
