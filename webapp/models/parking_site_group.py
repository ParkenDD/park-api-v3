"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Index

from webapp.extensions import db

from .base import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite
    from .source import Source


class ParkingSiteGroup(BaseModel):
    __tablename__ = 'parking_site_group'

    __table_args__ = (
        Index(
            'ix_parking_site_group_source_original_uid',
            'source_id',
            'original_uid',
            unique=True,
        ),
    )

    source: Mapped['Source'] = relationship('Source', back_populates='parking_site_groups')
    parking_sites: Mapped[list['ParkingSite']] = relationship('ParkingSite', back_populates='parking_site_group')

    source_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey('source.id'), nullable=False)
    original_uid: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
