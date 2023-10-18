"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper
from webapp.common.logger import Logger


class AdminApiBaseHandler:
    """
    Base class for API handler classes (`auth.AuthHandler`, etc.)
    """

    logger: Logger
    config_helper: ConfigHelper
    event_helper: EventHelper

    def __init__(self, logger: Logger, config_helper: ConfigHelper, event_helper: EventHelper):
        self.logger = logger
        self.config_helper = config_helper
        self.event_helper = event_helper
