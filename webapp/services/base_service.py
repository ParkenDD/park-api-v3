"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper
from webapp.common.logging import Logger


class BaseService(ABC):
    logger: Logger
    config_helper: ConfigHelper
    event_helper: EventHelper

    def __init__(self, *, logger: Logger, config_helper: ConfigHelper, event_helper: EventHelper):
        self.logger = logger
        self.config_helper = config_helper
        self.event_helper = event_helper

    def get_default_dependencies(self):
        return {
            'logger': self.logger,
            'config_helper': self.config_helper,
            'event_helper': self.event_helper,
        }
