"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper


class PublicApiBaseHandler:
    """
    Base class for API handler classes (`auth.AuthHandler`, etc.)
    """

    config_helper: ConfigHelper
    event_helper: EventHelper

    def __init__(self, config_helper: ConfigHelper, event_helper: EventHelper):
        self.config_helper = config_helper
        self.event_helper = event_helper
