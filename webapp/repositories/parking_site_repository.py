"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from parkapi_sources.models.enums import PurposeType
from sqlalchemy import func, select
from sqlalchemy.orm import Query, joinedload, selectinload
from validataclass_search_queries.filters import BoundSearchFilter
from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models import ParkingSite, Source
from webapp.repositories import BaseRepository


@dataclass
class ParkingSiteLocation:
    id: int
    source_id: int
    lat: float
    lon: float
    purpose: PurposeType


class ParkingSiteRepository(BaseRepository):
    model_cls = ParkingSite

    def fetch_parking_sites(
        self,
        *,
        search_query: Optional[BaseSearchQuery] = None,
        include_restricted_to: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
        include_source: bool = True,
        include_parking_site_group: bool = False,
    ) -> PaginatedResult[ParkingSite]:
        query = self.session.query(ParkingSite)

        if include_source:
            query = query.options(joinedload(ParkingSite.source))
        if include_restricted_to:
            query = query.options(selectinload(ParkingSite.restricted_to))
        if include_external_identifiers:
            query = query.options(selectinload(ParkingSite.external_identifiers))
        if include_tags:
            query = query.options(selectinload(ParkingSite.tags))
        if include_parking_site_group:
            query = query.options(joinedload(ParkingSite.parking_site_group))

        return self._search_and_paginate(query, search_query)

    def fetch_parking_site_by_id(
        self,
        parking_site_id: int,
        include_restricted_to: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
    ):
        load_options = []
        if include_restricted_to:
            load_options.append(selectinload(ParkingSite.restricted_to))
        if include_external_identifiers:
            load_options.append(selectinload(ParkingSite.external_identifiers))
        if include_tags:
            load_options.append(selectinload(ParkingSite.tags))

        return self.fetch_resource_by_id(parking_site_id, load_options=load_options)

    def fetch_parking_site_by_ids(
        self,
        parking_site_ids: list[int],
        *,
        include_sources: bool = False,
    ) -> list[ParkingSite]:
        query = self.session.query(ParkingSite).filter(ParkingSite.id.in_(parking_site_ids))

        if include_sources:
            query = query.options(joinedload(ParkingSite.source))

        return query.all()

    def fetch_parking_site_by_source_id_and_external_uid(self, source_id: int, original_uid: str) -> ParkingSite:
        parking_site: ParkingSite | None = (
            self.session.query(ParkingSite)
            .filter(ParkingSite.source_id == source_id)
            .filter(ParkingSite.original_uid == original_uid)
            .first()
        )

        return self._or_raise(
            parking_site,
            f'ParkingSite with source id {source_id} and original_uid {original_uid} not found',
        )

    def fetch_parking_site_ids_by_source_id(self, source_id: int) -> list[int]:
        return self.session.scalars(select(ParkingSite.id).where(ParkingSite.source_id == source_id)).all()

    def fetch_realtime_outdated_parking_site_count_by_source(self, older_then: datetime) -> dict[int, int]:
        query = self.session.query(ParkingSite.source_id, func.count(ParkingSite.id))

        query = query.filter(ParkingSite.realtime_data_updated_at < older_then)

        result = query.group_by(ParkingSite.source_id).all()

        return {key: value for key, value in result}

    def count_by_source(self) -> dict[int, int]:
        result: dict[int, int] = {}
        parking_sites = (
            self.session.query(ParkingSite.source_id, func.count(ParkingSite.id).label('count'))
            .group_by(ParkingSite.source_id)
            .all()
        )
        for parking_site in parking_sites:
            result[parking_site.source_id] = parking_site.count

        return result

    def save_parking_site(self, parking_site: ParkingSite, *, commit: bool = True):
        self._save_resources(parking_site, commit=commit)

    def delete_parking_site(self, parking_site: ParkingSite, *, commit: bool = True):
        self._delete_resources(parking_site, commit=commit)

    def _filter_by_search_query(self, query: Query, search_query: Optional[BaseSearchQuery]) -> Query:
        if search_query is None:
            return query

        # Apply all search filters one-by-one
        for _param_name, bound_filter in search_query.get_search_filters():
            if _param_name in ['location', 'radius', 'lat', 'lon']:
                continue
            query = self._apply_bound_search_filter(query, bound_filter)

        # Support old (unit: km, location field) and new (unit: m, dedicated lat/lon fields) radius search
        lat = None
        lon = None
        radius = None
        if hasattr(search_query, 'radius') and search_query.radius:
            radius = float(search_query.radius)
        if hasattr(search_query, 'location') and search_query.location:
            lat = float(search_query.location[1])
            lon = float(search_query.location[0])
            radius = radius * 1000
        elif hasattr(search_query, 'lat') and search_query.lat and hasattr(search_query, 'lon') and search_query.lon:
            lat = float(search_query.lat)
            lon = float(search_query.lon)

        if lat is not None and lon is not None and radius is not None:
            engine_name = self.session.connection().dialect.name
            if engine_name == 'postgresql':
                distance_function = func.ST_DistanceSphere(
                    ParkingSite.geometry,
                    func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326),
                )
            elif engine_name == 'mysql':
                distance_function = func.ST_DISTANCE_SPHERE(
                    ParkingSite.geometry,
                    func.ST_GeomFromText(f'POINT({lon} {lat})', 4326),
                )
            else:
                raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')
            query = query.filter(distance_function < int(radius))

        return query

    def _apply_bound_search_filter(self, query: Query, bound_filter: BoundSearchFilter) -> Query:
        if bound_filter.param_name == 'source_uid':
            return query.join(Source, Source.id == ParkingSite.source_id).filter(Source.uid == bound_filter.value)
        if bound_filter.param_name == 'source_uids':
            return query.join(Source, Source.id == ParkingSite.source_id).filter(Source.uid.in_(bound_filter.value))
        if bound_filter.param_name == 'ignore_duplicates':
            if bound_filter.value is False:
                return query
            return query.filter(ParkingSite.duplicate_of_parking_site_id.is_(None))
        if bound_filter.param_name == 'not_type':
            return query.filter(ParkingSite.type != bound_filter.value)
        return super()._apply_bound_search_filter(query, bound_filter)

    def fetch_parking_site_locations(self) -> list[ParkingSiteLocation]:
        query = self.session.query(
            ParkingSite.id,
            ParkingSite.lat,
            ParkingSite.lon,
            ParkingSite.source_id,
            ParkingSite.purpose,
        )

        result: list[ParkingSiteLocation] = []
        for item in query.all():
            result.append(
                ParkingSiteLocation(
                    id=item.id,
                    source_id=item.source_id,
                    purpose=item.purpose,
                    lat=float(item.lat),
                    lon=float(item.lon),
                ),
            )
        return result
