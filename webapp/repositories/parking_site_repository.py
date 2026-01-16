"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from parkapi_sources.models.enums import PurposeType
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Query, aliased, joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption
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
        **kwargs,
    ) -> PaginatedResult[ParkingSite]:
        query = self.session.query(ParkingSite)

        loader_options = self._get_loader_options(**kwargs)
        if loader_options:
            query = query.options(*loader_options)

        return self._search_and_paginate(query, search_query)

    def fetch_parking_site_by_id(
        self,
        parking_site_id: int,
        **kwargs,
    ):
        load_options = self._get_loader_options(**kwargs)
        return self.fetch_resource_by_id(parking_site_id, load_options=load_options)

    def fetch_parking_site_by_source_uid_and_original_uid(
        self, source_uid: str, original_uid: str, **kwargs
    ) -> ParkingSite:
        query = self.session.query(ParkingSite)

        load_options = self._get_loader_options(**kwargs)
        if load_options:
            query = query.options(*load_options)

        query = query.join(ParkingSite.source)
        query = query.filter(Source.uid == source_uid, ParkingSite.original_uid == original_uid)

        return self._or_raise(
            query.one_or_none(), f'ParkingSite with source uid {source_uid} and original_uid {original_uid} not found'
        )

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

    def fetch_parking_site_by_source_id_and_original_uid(
        self,
        source_id: int,
        original_uid: str,
        **kwargs,
    ) -> ParkingSite:
        query = self.session.query(ParkingSite)

        load_options = self._get_loader_options(**kwargs)
        if load_options:
            query = query.options(*load_options)

        query = query.filter(ParkingSite.source_id == source_id, ParkingSite.original_uid == original_uid)

        return self._or_raise(
            query.one_or_none(),
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
            if _param_name in ['location', 'radius', 'lat', 'lon', 'lat_min', 'lat_max', 'lon_min', 'lon_max']:
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

        if (
            getattr(search_query, 'lat_min', None)
            and getattr(search_query, 'lat_max', None)
            and getattr(search_query, 'lon_min', None)
            and getattr(search_query, 'lon_max', None)
        ):
            query = query.filter(
                func.ST_Within(
                    ParkingSite.geometry,
                    func.ST_MakeEnvelope(
                        getattr(search_query, 'lon_min'),
                        getattr(search_query, 'lat_min'),
                        getattr(search_query, 'lon_max'),
                        getattr(search_query, 'lat_max'),
                        4326,
                    ),
                ),
            )

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

    def fetch_parking_sites_duplicates(self, source_ids: list[int] | None = None) -> list[tuple[int, int]]:
        query = self.session.query(ParkingSite.id, ParkingSite.duplicate_of_parking_site_id)

        query = query.filter(ParkingSite.duplicate_of_parking_site_id.isnot(None))

        if source_ids is not None:
            duplicate_parking_site = aliased(ParkingSite)
            query = query.join(
                duplicate_parking_site, duplicate_parking_site.id == ParkingSite.duplicate_of_parking_site_id
            )
            query = query.filter(
                or_(
                    ParkingSite.source_id.in_(source_ids),
                    duplicate_parking_site.source_id.in_(source_ids),
                )
            )

        result: list[tuple[int, int]] = []
        for item in query.all():
            result.append((item.id, item.duplicate_of_parking_site_id))

        return result

    @staticmethod
    def _get_loader_options(
        *,
        include_restrictions: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
        include_source: bool = True,
        include_parking_site_group: bool = False,
    ) -> list[LoaderOption]:
        loader_options: list[LoaderOption] = []
        if include_source:
            loader_options.append(joinedload(ParkingSite.source))
        if include_restrictions:
            loader_options.append(selectinload(ParkingSite.restrictions))
        if include_external_identifiers:
            loader_options.append(selectinload(ParkingSite.external_identifiers))
        if include_tags:
            loader_options.append(selectinload(ParkingSite.tags))
        if include_parking_site_group:
            loader_options.append(joinedload(ParkingSite.parking_site_group))

        return loader_options
