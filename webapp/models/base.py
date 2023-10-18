"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utc import UtcDateTime
from typing_extensions import Self

from webapp.common.events import Event, EventSource, EventType
from webapp.common.sqlalchemy import ModelEventAction
from webapp.extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
    }

    event_prefix: Optional[str] = None
    event_parameter: Optional[str] = None

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
        index=True,
    )
    modified_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
        index=True,
    )

    def to_dict(self, fields: Optional[list[str]] = None, ignore: Optional[list[str]] = None) -> dict:
        result = {}
        for field in self.metadata.tables[self.__tablename__].c.keys():
            if fields is not None and field not in fields:
                continue
            if ignore is not None and field in ignore:
                continue
            result[field] = getattr(self, field)
        return result

    def from_dict(self, data: dict, include_id: bool = True) -> Self:
        for field in self.metadata.tables[self.__tablename__].c.keys():
            if field == 'id' and not include_id:
                continue
            if field not in data:
                continue
            setattr(self, field, data[field])
        return self

    def get_events(self, action: ModelEventAction) -> list[Event]:
        if self.event_prefix is None or self.event_parameter is None:
            return []
        return [
            Event(
                type=EventType[f'{self.event_prefix}_{action.name}'],
                source=EventSource.ORM,
                data={self.event_parameter: self.id},
            )
        ]
