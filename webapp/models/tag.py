"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.extensions import db
from webapp.models import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite


class Tag(BaseModel):
    __tablename__ = 'tag'

    parking_site: Mapped['ParkingSite'] = relationship('ParkingSite', back_populates='tags')

    parking_site_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey('parking_site.id'), nullable=False)
    value: Mapped[str] = mapped_column(String(256), nullable=False)
