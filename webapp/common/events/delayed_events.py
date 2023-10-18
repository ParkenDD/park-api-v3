"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.extensions import celery

from .enum import EventSource, EventType


@celery.task
def trigger_delayed_event(event_type: str, event_source_str: str, event_id: int, data: dict):
    from webapp.dependencies import dependencies

    dependencies.get_event_helper().trigger_async(
        event_type=EventType[event_type],
        event_source=EventSource[event_source_str],
        event_id=event_id,
        data=data,
    )
