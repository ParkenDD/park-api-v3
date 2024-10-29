"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime

from .base import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite
    from .parking_site_group import ParkingSiteGroup


class SourceStatus(PythonEnum):
    DISABLED = 'DISABLED'
    ACTIVE = 'ACTIVE'
    FAILED = 'FAILED'
    PROVISIONED = 'PROVISIONED'


class Source(BaseModel):
    __tablename__ = 'source'

    parking_sites: Mapped[list['ParkingSite']] = relationship(
        'ParkingSite',
        back_populates='source',
        cascade='all, delete, delete-orphan',
    )
    parking_site_groups: Mapped[list['ParkingSiteGroup']] = relationship(
        'ParkingSiteGroup',
        back_populates='source',
        cascade='all, delete, delete-orphan',
    )

    uid: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    public_url: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)

    static_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)
    realtime_data_updated_at: Mapped[Optional[datetime]] = mapped_column(UtcDateTime(), nullable=True)

    attribution_license: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    attribution_contributor: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    attribution_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    static_status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus),
        nullable=False,
        default=SourceStatus.PROVISIONED,
    )
    realtime_status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus),
        nullable=False,
        default=SourceStatus.PROVISIONED,
    )

    static_parking_site_error_count: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    realtime_parking_site_error_count: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)

    @property
    def combined_status(self) -> SourceStatus:
        if self.static_status != SourceStatus.ACTIVE or self.realtime_status in [
            SourceStatus.PROVISIONED,
            SourceStatus.DISABLED,
        ]:
            return self.static_status
        return self.realtime_status

    @property
    def combined_updated_at(self) -> datetime:
        if self.static_data_updated_at and self.realtime_data_updated_at:
            return max(self.static_data_updated_at, self.realtime_data_updated_at)
        if self.realtime_data_updated_at:
            return self.realtime_data_updated_at
        if self.static_data_updated_at:
            return self.static_data_updated_at
        return self.modified_at
