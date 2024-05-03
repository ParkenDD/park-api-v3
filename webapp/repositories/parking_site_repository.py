"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, joinedload, selectinload
from validataclass_search_queries.filters import BoundSearchFilter
from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models import ParkingSite, Source
from webapp.repositories import BaseRepository
from webapp.repositories.exceptions import ObjectNotFoundException


class ParkingSiteRepository(BaseRepository):
    model_cls = ParkingSite

    def fetch_parking_sites(
        self,
        *,
        search_query: Optional[BaseSearchQuery] = None,
        include_external_identifiers: bool = False,
        include_source: bool = True,
    ) -> PaginatedResult[ParkingSite]:
        query = self.session.query(ParkingSite)

        if include_source:
            query.options(joinedload(ParkingSite.source))
        if include_external_identifiers:
            query.options(selectinload(ParkingSite.external_identifiers))

        return self._search_and_paginate(query, search_query)

    def fetch_parking_site_by_id(self, parking_site_id: int):
        return self.fetch_resource_by_id(parking_site_id)

    def fetch_parking_site_by_source_id_and_external_uid(self, source_id: int, original_uid: str) -> ParkingSite:
        parking_site: Optional[ParkingSite] = (
            self.session.query(ParkingSite)
            .filter(ParkingSite.source_id == source_id)
            .filter(ParkingSite.original_uid == original_uid)
            .first()
        )

        if not parking_site:
            raise ObjectNotFoundException(message=f'ParkingSite with source id {source_id} and original_uid {original_uid} not found')

        return parking_site

    def save_parking_site(self, parking_site: ParkingSite, *, commit: bool = True):
        self._save_resources(parking_site, commit=commit)

    def delete_parking_site(self, parking_site: ParkingSite):
        self._delete_resources(parking_site)

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
        return super()._apply_bound_search_filter(query, bound_filter)
