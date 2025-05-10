"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import timezone
from typing import Optional

from validataclass.helpers import BaseDateTimeRange
from validataclass.validators import DateTimeFormat, DateTimeValidator


class DateTimeToUtcValidator(DateTimeValidator):
    """
    Custom DateTimeValidator with preset parameters that allows any datetime (with and without timezone information)
    and always converts the result to UTC. Datetimes without timezone will be interpreted as UTC.

    Milli- and microseconds will be automatically discarded by default (set `discard_milliseconds=False` to disable this).

    The following examples are all valid and result in the same datetime ("2021-12-31T12:34:56+00:00"):

    ```
    2021-12-31T12:34:56
    2021-12-31T12:34:56Z
    2021-12-31T12:34:56+00:00
    2021-12-31T14:34:56+02:00
    2021-12-31T14:34:56.123+02:00
    2021-12-31T14:34:56.123456+02:00
    ```
    """

    def __init__(self, *, discard_milliseconds: bool = True, datetime_range: Optional[BaseDateTimeRange] = None):
        super().__init__(
            DateTimeFormat.ALLOW_TIMEZONE,
            discard_milliseconds=discard_milliseconds,
            local_timezone=timezone.utc,
            target_timezone=timezone.utc,
            datetime_range=datetime_range,
        )
