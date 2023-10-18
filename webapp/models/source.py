"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime

from .base import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite


class Source(BaseModel):
    __tablename__ = 'source'

    parking_sites: Mapped['ParkingSite'] = relationship('ParkingSite', back_populates='source')

    uid: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    public_url: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    last_import: Mapped[Optional[datetime]] = mapped_column(UtcDateTime, nullable=True)

    attribution_license: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    attribution_contributor: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    attribution_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
