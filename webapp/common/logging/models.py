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
    FAILED_SOURCE_HANDLING = 'failed-source-handling'
    FAILED_STATIC_SOURCE_HANDLING = 'failed-static-source-handling'
    FAILED_REALTIME_SOURCE_HANDLING = 'failed-realtime-source-handling'
    FAILED_PARKING_SITE_HANDLING = 'failed-parking-site-handling'
    FAILED_STATIC_PARKING_SITE_HANDLING = 'failed-static-parking-site-handling'
    FAILED_REALTIME_PARKING_SITE_HANDLING = 'failed-realtime-parking-site-handling'
    DUPLICATE_HANDLING = 'duplicate-handling'
    MISC = 'misc'


class LogTag(Enum):
    SOURCE = 'source'
    PARKING_SITE = 'parking-site'
    INITIATOR = 'initiator'
    USER = 'user'
