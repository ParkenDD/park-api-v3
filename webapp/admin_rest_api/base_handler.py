"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper
from webapp.models import Source
from webapp.models.source import SourceStatus


class AdminApiBaseHandler:
    """
    Base class for API handler classes (`auth.AuthHandler`, etc.)
    """

    config_helper: ConfigHelper
    event_helper: EventHelper

    def __init__(self, config_helper: ConfigHelper, event_helper: EventHelper):
        self.config_helper = config_helper
        self.event_helper = event_helper

    @staticmethod
    def _update_source_status_after_push(source: Source, has_static_data: bool, has_realtime_data: bool):
        """
        Make sure that source status and timestamps reflect a push, independent of the import service internals.
        """
        now = datetime.now(tz=timezone.utc)

        if has_static_data:
            source.static_status = SourceStatus.ACTIVE
            source.static_data_updated_at = now

        # Realtime data is only applied if static data is active, so realtime status is only updated in this case
        if has_realtime_data and source.static_status == SourceStatus.ACTIVE:
            source.realtime_status = SourceStatus.ACTIVE
            source.realtime_data_updated_at = now
