"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum


class TelemetryContext(Enum):
    SOURCE = 'source'
    PARKING_SITE = 'parking-site'
    INITIATOR = 'initiator'
    USER = 'user'
