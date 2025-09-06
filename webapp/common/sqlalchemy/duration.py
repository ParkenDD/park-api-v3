"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import timedelta
from typing import Any

from isodate import Duration, ISO8601Error, duration_isoformat, parse_duration
from sqlalchemy import Dialect, String, TypeDecorator


class SqlalchemyDuration(TypeDecorator):
    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Dialect):
        if isinstance(value, Duration) or isinstance(value, timedelta):
            return duration_isoformat(value)
        return value

    def process_result_value(self, value: Any, dialect: Dialect):
        if isinstance(value, str):
            try:
                return parse_duration(value)
            except ISO8601Error:
                # Try again by parsing pure duration format:
                try:
                    parse_duration(f'PT{value}')
                except ISO8601Error:
                    return None
        return value

    def __repr__(self):
        return self.impl.__repr__()
