"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING, Optional

from isodate import Duration
from parkapi_sources.models.enums import ParkingAudience
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy import Enum as SqlalchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.common.sqlalchemy import SqlalchemyDuration

from .base import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite
    from .parking_spot import ParkingSpot


class ParkingRestriction(BaseModel):
    __tablename__ = 'parking_restriction'

    parking_site: Mapped[Optional['ParkingSite']] = relationship('ParkingSite', back_populates='restrictions')
    parking_spot: Mapped[Optional['ParkingSpot']] = relationship('ParkingSpot', back_populates='restrictions')

    parking_site_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('parking_site.id'), nullable=True)
    parking_spot_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('parking_spot.id'), nullable=True)

    type: Mapped[ParkingAudience | None] = mapped_column(SqlalchemyEnum(ParkingAudience), nullable=True)
    hours: Mapped[str | None] = mapped_column(String(512), nullable=True)
    max_stay: Mapped[Duration | None] = mapped_column(SqlalchemyDuration, nullable=True)

    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    realtime_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    realtime_free_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
