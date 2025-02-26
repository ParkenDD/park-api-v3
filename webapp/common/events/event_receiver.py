"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .enum import EventSource, EventType


class EventReceiver(ABC):
    """
    This class is the entrypoint for a event. Usually it initializes a service class with all its dependencies and
    runs the desired method.
    """

    run_async: bool = False
    delay_seconds: Optional[int] = None
    listen_to_event_source: Optional[EventSource] = None

    @property
    @abstractmethod
    def listen_to_event_types(self) -> List[EventType]:
        pass

    @property
    @abstractmethod
    def required_parameters(self) -> List[str]:
        pass

    def get_default_service_dependencies(
        self,
    ):  # TODO: move all services to dependencies to remove this
        from webapp.dependencies import dependencies

        return {
            'config_helper': dependencies.get_config_helper(),
            'event_helper': dependencies.get_event_helper(),
        }

    @abstractmethod
    def run(self, event_source: EventSource, data: dict):
        pass
