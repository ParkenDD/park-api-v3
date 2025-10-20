"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Integer
from sqlalchemy import Enum as SqlalchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime

from webapp.extensions import db

from .base import BaseModel
from .parking_site import OpeningStatus, ParkingSite


class ParkingSiteHistory(BaseModel):
    __tablename__ = 'parking_site_history'

    parking_site: Mapped['ParkingSite'] = relationship('ParkingSite', back_populates='parking_site_history')
    parking_site_id: Mapped[int] = mapped_column(BigInteger(), db.ForeignKey('parking_site.id'), nullable=False)

    static_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)
    realtime_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)
    realtime_opening_status: Mapped[OpeningStatus | None] = mapped_column(
        SqlalchemyEnum(OpeningStatus), nullable=True, default=None
    )

    capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    # Deprecated fields
    capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    realtime_capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    realtime_free_capacity_disabled: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_woman: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_family: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_charging: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_carsharing: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_truck: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    realtime_free_capacity_bus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
