"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum


class LogMessageType(Enum):
    REQUEST_IN = 'request-in'
    REQUEST_OUT = 'request-out'
    DATABASE_CREATE = 'database-create'
    DATABASE_UPDATE = 'database-update'
    DATABASE_DELETE = 'database-delete'
    EXCEPTION = 'exception'
    SOURCE_HANDLING = 'source-handling'
    STATIC_SOURCE_HANDLING = 'static-source-handling'
    REALTIME_SOURCE_HANDLING = 'realtime-source-handling'
    PARKING_SITE_HANDLING = 'parking-site-handling'
    STATIC_PARKING_SITE_HANDLING = 'static-parking-site-handling'
    REALTIME_PARKING_SITE_HANDLING = 'failed-realtime-parking-site-handling'
    STATIC_PARKING_SPOT_HANDLING = 'failed-static-parking-spot-handling'
    REALTIME_PARKING_SPOT_HANDLING = 'failed-realtime-parking-spot-handling'
    DUPLICATE_HANDLING = 'duplicate-handling'
    MISC = 'misc'
