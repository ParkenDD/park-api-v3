"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING, Optional

from parkapi_sources.models.enums import ExternalIdentifierType
from sqlalchemy import BigInteger, String
from sqlalchemy import (
    Enum as SqlalchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.extensions import db
from webapp.models import BaseModel

if TYPE_CHECKING:
    from .parking_site import ParkingSite


class ExternalIdentifier(BaseModel):
    __tablename__ = 'external_identifier'

    parking_site: Mapped[Optional['ParkingSite']] = relationship('ParkingSite', back_populates='external_identifiers')
    parking_spot: Mapped[Optional['ParkingSite']] = relationship('ParkingSpot', back_populates='external_identifiers')

    parking_site_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey('parking_site.id'), nullable=True)
    parking_spot_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey('parking_spot.id'), nullable=True)

    value: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[ExternalIdentifierType] = mapped_column(SqlalchemyEnum(ExternalIdentifierType), nullable=False)
