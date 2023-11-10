"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum


class EventSource(Enum):
    CLIENT_API = 'CLIENT_API'
    CLI = 'CLI'
    ORM = 'ORM'
    SERVER_API = 'SERVER_API'
    SERVICE = 'SERVICE'


class EventType(Enum):
    OPTION_CREATED = 'OPTION_CREATED'
    OPTION_UPDATED = 'OPTION_UPDATED'
    OPTION_DELETED = 'OPTION_DELETED'
