"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from parkapi_sources.models.enums import ParkingSpotStatus, ParkingSpotType, PurposeType
from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    event,
    func,
)
from sqlalchemy import (
    Enum as SqlalchemyEnum,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime

from webapp.common.dataclass import filter_unset_value_and_none
from webapp.common.json import DefaultJSONEncoder
from webapp.common.sqlalchemy.point import Point
from webapp.extensions import db

from .base import BaseModel

if TYPE_CHECKING:
    from .external_identifier import ExternalIdentifier
    from .parking_restriction import ParkingRestriction
    from .parking_site import ParkingSite
    from .source import Source
    from .tag import Tag


class ParkingSpot(BaseModel):
    __tablename__ = 'parking_spot'
    __table_args__ = (
        Index(
            'ix_parking_spot_source_original_uid',
            'source_id',
            'original_uid',
            unique=True,
        ),
    )

    source: Mapped['Source'] = relationship('Source', back_populates='parking_spots')
    parking_site: Mapped[Optional['ParkingSite']] = relationship('ParkingSite', back_populates='parking_spots')
    restrictions: Mapped[list['ParkingRestriction']] = relationship(
        'ParkingRestriction',
        back_populates='parking_spot',
        cascade='all, delete-orphan',
    )
    external_identifiers: Mapped[list['ExternalIdentifier']] = relationship(
        'ExternalIdentifier',
        back_populates='parking_spot',
        cascade='all, delete-orphan',
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        back_populates='parking_spot',
        cascade='all, delete-orphan',
    )

    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('source.id'), nullable=False)
    parking_site_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('parking_site.id'), nullable=True)

    original_uid: Mapped[str] = mapped_column(String(256), index=True, nullable=False)

    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    type: Mapped[ParkingSpotType | None] = mapped_column(SqlalchemyEnum(ParkingSpotType), nullable=True)
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lat: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    lon: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    _geojson: Mapped[str | None] = mapped_column('geojson', Text, nullable=True)
    purpose: Mapped[PurposeType] = mapped_column(SqlalchemyEnum(PurposeType), nullable=False, index=True)

    realtime_status: Mapped[ParkingSpotStatus | None] = mapped_column(SqlalchemyEnum(ParkingSpotStatus), nullable=True)

    static_data_updated_at: Mapped[datetime] = mapped_column(UtcDateTime(), nullable=False)
    realtime_data_updated_at: Mapped[datetime] = mapped_column(UtcDateTime(), nullable=True)

    has_realtime_data: Mapped[bool] = mapped_column(Boolean, nullable=False)

    geometry: Mapped[bytes] = mapped_column(Point(), nullable=False)

    @hybrid_property
    def geojson(self) -> Mapped[dict | None]:
        if self._geojson is None:
            return None
        return json.loads(self._geojson)

    @geojson.setter
    def geojson(self, geojson: dict | None = None) -> None:
        if geojson is None:
            self._geojson = None
        else:
            self._geojson = json.dumps(geojson, cls=DefaultJSONEncoder)

    def to_dict(
        self,
        fields: Optional[list[str]] = None,
        include_restrictions: bool = False,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
        ignore: Optional[list[str]] = None,
    ) -> dict:
        if ignore is None:
            ignore = []
        # Geometry is an internal geo-indexed field, so it should not be part of the default output
        ignore.append('geometry')

        result = super().to_dict(fields, ignore)

        if include_restrictions and len(self.restrictions):
            result['restrictions'] = []
            for parking_restriction in self.restrictions:
                result['restrictions'].append(parking_restriction.to_dict(fields=['type', 'hours', 'max_stay']))

            # Legacy output
            result['restricted_to'] = []
            for parking_restriction in self.restrictions:
                result['restricted_to'].append(parking_restriction.to_dict(fields=['type', 'hours', 'max_stay']))

        if include_external_identifiers and len(self.external_identifiers):
            result['external_identifiers'] = []
            for external_identifier in self.external_identifiers:
                result['external_identifiers'].append({
                    'type': external_identifier.type,
                    'value': external_identifier.value,
                })

        if include_tags and len(self.tags):
            result['tags'] = []
            for tag in self.tags:
                result['tags'].append(tag.value)

        return filter_unset_value_and_none(result)


@event.listens_for(ParkingSpot, 'before_insert')
@event.listens_for(ParkingSpot, 'before_update')
def set_geometry(mapper, connection, parking_spot: ParkingSpot):
    lat_history = db.inspect(parking_spot).attrs.lat.history
    lon_history = db.inspect(parking_spot).attrs.lon.history

    # just update when there are changes in lat or lon
    if (
        (lat_history[0] and len(lat_history[0]))
        or (lat_history[2] and len(lat_history[2]))
        or (lon_history[0] and len(lon_history[0]))
        or (lon_history[2] and len(lon_history[2]))
    ):
        engine_name = db.session.get_bind().dialect.name
        if engine_name == 'postgresql':
            parking_spot.geometry = func.ST_SetSRID(
                func.ST_MakePoint(float(parking_spot.lon), float(parking_spot.lat)),
                4326,
            )
        elif engine_name == 'mysql':
            parking_spot.geometry = func.ST_GeomFromText(
                f'POINT({float(parking_spot.lat)} {float(parking_spot.lon)})',
                4326,
            )
        else:
            raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')
