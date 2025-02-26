"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from webapp.common.config import ConfigHelper
from webapp.common.contexts import ContextHelper
from webapp.common.events import EventHelper


class BaseService(ABC):
    config_helper: ConfigHelper
    context: ContextHelper
    event_helper: EventHelper

    def __init__(self, *, config_helper: ConfigHelper, context_helper: ContextHelper, event_helper: EventHelper):
        self.config_helper = config_helper
        self.context_helper = context_helper
        self.event_helper = event_helper

    def get_default_dependencies(self):
        return {
            'config_helper': self.config_helper,
            'context_helper': self.context_helper,
            'event_helper': self.event_helper,
        }
