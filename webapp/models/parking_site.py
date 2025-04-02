"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    event,
    func,
)
from sqlalchemy import (
    Enum as SqlalchemyEnum,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Index
from sqlalchemy_utc import UtcDateTime

from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingSiteType, PurposeType, SupervisionType
from webapp.common.dataclass import filter_unset_value_and_none
from webapp.common.sqlalchemy.point import Point
from webapp.extensions import db

from .base import BaseModel

if TYPE_CHECKING:
    from .external_identifier import ExternalIdentifier
    from .parking_restriction import ParkingRestriction
    from .parking_site_group import ParkingSiteGroup
    from .parking_site_history import ParkingSiteHistory
    from .parking_spot import ParkingSpot
    from .source import Source
    from .tag import Tag


class ParkingSite(BaseModel):
    __tablename__ = 'parking_site'

    __table_args__ = (
        Index(
            'ix_parking_site_source_original_uid',
            'source_id',
            'original_uid',
            unique=True,
        ),
    )

    source: Mapped['Source'] = relationship('Source', back_populates='parking_sites')
    external_identifiers: Mapped[list['ExternalIdentifier']] = relationship(
        'ExternalIdentifier',
        back_populates='parking_site',
        cascade='all, delete-orphan',
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        back_populates='parking_site',
        cascade='all, delete-orphan',
    )
    parking_spots: Mapped[list['ParkingSpot']] = relationship(
        'ParkingSpot',
        back_populates='parking_site',
        cascade='all, delete-orphan',
    )
    restricted_to: Mapped[list['ParkingRestriction']] = relationship(
        'ParkingRestriction',
        back_populates='parking_site',
        cascade='all, delete-orphan',
    )
    parking_site_history: Mapped[list['ParkingSiteHistory']] = relationship(
        'ParkingSiteHistory',
        back_populates='parking_site',
        cascade='all, delete-orphan',
    )
    parking_site_group: Mapped['ParkingSiteGroup'] = relationship(
        'ParkingSiteGroup',
        back_populates='parking_sites',
    )

    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('source.id'), nullable=False)
    parking_site_group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('parking_site_group.id'),
        nullable=True,
    )
    duplicate_of_parking_site_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('parking_site.id'),
        nullable=True,
    )
    original_uid: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    operator_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    public_url: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    type: Mapped[Optional[ParkingSiteType]] = mapped_column(SqlalchemyEnum(ParkingSiteType), nullable=True)
    purpose: Mapped[PurposeType] = mapped_column(SqlalchemyEnum(PurposeType), nullable=False, index=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)

    max_stay: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    max_height: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    max_width: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    has_lighting: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True)
    is_covered: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True)
    fee_description: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    has_fee: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True)
    _park_and_ride_type: Mapped[Optional[str]] = mapped_column('park_and_ride_type', String(256), nullable=True)
    supervision_type: Mapped[Optional[SupervisionType]] = mapped_column(SqlalchemyEnum(SupervisionType), nullable=True)
    related_location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    has_realtime_data: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=False, default=False)
    static_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)
    realtime_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)
    realtime_opening_status: Mapped[OpeningStatus | None] = mapped_column(
        SqlalchemyEnum(OpeningStatus),
        nullable=True,
        default=None,
    )

    lat: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    lon: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)

    capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    realtime_capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    realtime_free_capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    opening_hours: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    geometry: Mapped[bytes] = mapped_column(Point(), nullable=False)

    def to_dict(
        self,
        fields: Optional[list[str]] = None,
        ignore: Optional[list[str]] = None,
        include_external_identifiers: bool = False,
        include_tags: bool = False,
        include_group: bool = False,
    ) -> dict:
        if ignore is None:
            ignore = []
        # Geometry is an internal geo-indexed field, so it should not be part of the default output
        ignore.append('geometry')
        ignore.append('parking_site_group_id')

        result = super().to_dict(fields, ignore)

        # Add legacy field is_supervised
        if self.supervision_type is not None:
            result['is_supervised'] = self.supervision_type != SupervisionType.NO

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

        if include_group and self.parking_site_group:
            result['group'] = self.parking_site_group.to_dict(
                ignore=['parking_site_id'],
            )

        # If we don't have realtime support, we don't need realtime data
        if not self.has_realtime_data:
            return filter_unset_value_and_none(
                {key: value for key, value in result.items() if not key.startswith('realtime_')},
            )

        return filter_unset_value_and_none(result)

    @hybrid_property
    def park_and_ride_type(self) -> Mapped[Optional[list[ParkAndRideType]]]:
        if self._park_and_ride_type is None:
            return None
        return [ParkAndRideType[item] for item in self._park_and_ride_type.split('|')]

    @park_and_ride_type.setter
    def park_and_ride_type(self, park_and_ride_type: Optional[list[ParkAndRideType]]):
        if park_and_ride_type is None:
            self._park_and_ride_type = None
        else:
            self._park_and_ride_type = '|'.join([item.name for item in park_and_ride_type])


@event.listens_for(ParkingSite, 'before_insert')
@event.listens_for(ParkingSite, 'before_update')
def set_geometry(mapper, connection, parking_site: ParkingSite):
    lat_history = db.inspect(parking_site).attrs.lat.history
    lon_history = db.inspect(parking_site).attrs.lon.history

    # just update when there are changes in lat or lon
    if (
        (lat_history[0] and len(lat_history[0]))
        or (lat_history[2] and len(lat_history[2]))
        or (lon_history[0] and len(lon_history[0]))
        or (lon_history[2] and len(lon_history[2]))
    ):
        engine_name = db.session.get_bind().dialect.name
        if engine_name == 'postgresql':
            parking_site.geometry = func.ST_SetSRID(
                func.ST_MakePoint(float(parking_site.lon), float(parking_site.lat)),
                4326,
            )
        elif engine_name == 'mysql':
            parking_site.geometry = func.ST_GeomFromText(
                f'POINT({float(parking_site.lat)} {float(parking_site.lon)})',
                4326,
            )
        else:
            raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')
