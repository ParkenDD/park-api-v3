"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
from typing import Dict, List, Optional, Sequence

from webapp.common.celery import CeleryHelper
from webapp.common.contexts import ContextHelper
from webapp.common.logging.models import LogMessageType

from .delayed_events import trigger_delayed_event
from .enum import EventSource, EventType
from .event import Event
from .event_receiver import EventReceiver

logger = logging.getLogger(__name__)


class EventHelper:
    celery_helper: CeleryHelper
    # event_receivers is a list with service classes. The service entrypoint has to be a method called run.
    event_receivers: Dict[EventType, List[EventReceiver]]

    def __init__(self, celery_helper: CeleryHelper, context_helper: ContextHelper):
        self.celery_helper = celery_helper
        self.context_helper = context_helper
        self.event_receivers = {}

    def _get_event_queue(self) -> list:
        app_context = self.context_helper.get_app_context()
        if not hasattr(app_context, 'butterfly_events'):
            app_context.butterfly_events = []
        return app_context.butterfly_events

    def record(self, event: Event):
        self._get_event_queue().append(event)

    def publish_events(self):
        # deduplicate events from app context
        deduplicated_events = []
        for event in self._get_event_queue():
            if event not in deduplicated_events:
                deduplicated_events.append(event)

        # trigger deduplicated events
        for event in deduplicated_events:
            self.trigger(
                event_type=event.type,
                event_source=event.source,
                data=event.data,
            )

    def trigger(
        self,
        event_type: EventType,
        event_source: EventSource,
        data: Optional[dict] = None,
    ):
        """
        This function is for triggering events.
        Usually, it should not be used directly, instead Events should be recorded by record() and triggered together
        to ensure deduplication. But there might be situations where Events should be triggered directly, for example
        socket connections or long tasks.
        Because events are async it gives the event with its position in our event list to celery, then it will be
        triggered in our celery worker by trigger_async() below.
        """
        if event_type not in self.event_receivers:
            return

        for i in range(len(self.event_receivers[event_type])):
            # check for event source
            if (
                self.event_receivers[event_type][i].listen_to_event_source is not None
                and self.event_receivers[event_type][i].listen_to_event_source != event_source
            ):
                continue

            delay_seconds = self.event_receivers[event_type][i].delay_seconds
            if delay_seconds is None:
                delay_seconds = 0

            # push async events in celery queue which will trigger trigger_async() afterwards
            self.celery_helper.with_delay(
                task=trigger_delayed_event,
                delay_seconds=delay_seconds,
                event_type=event_type.name,
                event_source_str=event_source.name,
                event_id=i,
                data=data or {},
            )

    def trigger_async(
        self,
        event_type: EventType,
        event_source: EventSource,
        event_id: int,
        data: dict,
    ):
        for parameter in self.event_receivers[event_type][event_id].required_parameters:
            if parameter not in data:
                logger.error(
                    f'got event {event_type} with missing required parameters: {data}, '
                    f'required: {self.event_receivers[event_type][event_id].required_parameters}',
                    extra={'attributes': {'type': LogMessageType.EXCEPTION}},
                )
                return
        self.event_receivers[event_type][event_id].run(event_source=event_source, data=data)

    def register_receivers(self, event_receivers: Sequence[EventReceiver]):
        for event_receiver in event_receivers:
            for event_type in event_receiver.listen_to_event_types:
                if event_type not in self.event_receivers:
                    self.event_receivers[event_type] = []
                self.event_receivers[event_type].append(event_receiver)
