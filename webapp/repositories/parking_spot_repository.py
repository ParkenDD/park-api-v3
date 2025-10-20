"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
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
        include_restrictions: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
    ) -> PaginatedResult[ParkingSpot]:
        query = self.session.query(ParkingSpot)

        if include_source:
            query = query.options(joinedload(ParkingSpot.source))
        if include_restrictions:
            query = query.options(selectinload(ParkingSpot.restrictions))
        if include_external_identifiers:
            query = query.options(selectinload(ParkingSpot.external_identifiers))
        if include_tags:
            query = query.options(selectinload(ParkingSpot.tags))

        return self._search_and_paginate(query, search_query)

    def fetch_parking_spot_ids_by_source_id(self, source_id: int) -> list[int]:
        return self.session.scalars(select(ParkingSpot.id).where(ParkingSpot.source_id == source_id)).all()

    def fetch_parking_spot_by_id(
        self,
        parking_spot_id: int,
        include_source: bool = True,
        include_restrictions: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
    ) -> ParkingSpot:
        load_options = []
        if include_source:
            load_options.append(joinedload(ParkingSpot.source))
        if include_restrictions:
            load_options.append(selectinload(ParkingSpot.restrictions))
        if include_external_identifiers:
            load_options.append(selectinload(ParkingSpot.external_identifiers))
        if include_tags:
            load_options.append(selectinload(ParkingSpot.tags))

        return self.fetch_resource_by_id(parking_spot_id, load_options=load_options)

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

    def fetch_realtime_outdated_parking_spot_count_by_source(self, older_then: datetime) -> dict[int, int]:
        query = self.session.query(ParkingSpot.source_id, func.count(ParkingSpot.id))

        query = query.filter(ParkingSpot.realtime_data_updated_at < older_then)

        result = query.group_by(ParkingSpot.source_id).all()

        return {key: value for key, value in result}

    def count_by_source(self) -> dict[int, int]:
        result: dict[int, int] = {}
        parking_spots = (
            self.session.query(ParkingSpot.source_id, func.count(ParkingSpot.id).label('count'))
            .group_by(ParkingSpot.source_id)
            .all()
        )
        for parking_spot in parking_spots:
            result[parking_spot.source_id] = parking_spot.count

        return result

    def save_parking_spot(self, parking_spot: ParkingSpot, *, commit: bool = True):
        self._save_resources(parking_spot, commit=commit)

    def delete_parking_spot(self, parking_spot: ParkingSpot, *, commit: bool = True):
        self._delete_resources(parking_spot, commit=commit)

    def _filter_by_search_query(self, query: Query, search_query: Optional[BaseSearchQuery]) -> Query:
        if search_query is None:
            return query

        # Apply all search filters one-by-one
        for _param_name, bound_filter in search_query.get_search_filters():
            if _param_name in ['radius', 'lat', 'lon']:
                continue
            query = self._apply_bound_search_filter(query, bound_filter)

        if getattr(search_query, 'radius') and getattr(search_query, 'lat') and getattr(search_query, 'lon'):
            radius = float(getattr(search_query, 'radius'))
            lat = float(getattr(search_query, 'lat'))
            lon = float(getattr(search_query, 'lon'))

            engine_name = self.session.connection().dialect.name
            if engine_name == 'postgresql':
                distance_function = func.ST_DistanceSphere(
                    ParkingSpot.geometry,
                    func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326),
                )
            elif engine_name == 'mysql':
                distance_function = func.ST_DISTANCE_SPHERE(
                    ParkingSpot.geometry,
                    func.ST_GeomFromText(f'POINT({lon} {lat})', 4326),
                )
            else:
                raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')

            query = query.filter(distance_function < int(radius))

        return query

    def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
        if bound_filter.param_name == 'source_uid':
            return query.join(Source, Source.id == ParkingSpot.source_id).filter(Source.uid == bound_filter.value)
        if bound_filter.param_name == 'source_uids':
            return query.join(Source, Source.id == ParkingSpot.source_id).filter(Source.uid.in_(bound_filter.value))
        return super()._apply_bound_search_filter(query, bound_filter)
