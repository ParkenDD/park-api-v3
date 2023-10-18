"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass
from typing import Optional

from .enum import EventSource, EventType


@dataclass
class Event:
    type: EventType
    source: EventSource
    data: Optional[dict] = None
