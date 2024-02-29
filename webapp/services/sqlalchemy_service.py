"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, List, Tuple

from webapp.common.sqlalchemy import ModelEventAction

from .base_service import BaseService


class SqlalchemyService(BaseService):
    """
    This Service gets all Model changes ('insert', 'update', and 'delete') and generates Events based on these. This
    just works for simple redirections without SQL requests.
    If we want to remove Flask-SQLAlchemy, we need to adapt their recording-sql-event-code like this:
    https://stackoverflow.com/questions/32378878/run-function-after-a-certain-type-of-model-is-committed
    """

    def handle_model_changes(self, changes: List[Tuple[Any, str]]):
        for obj, action in changes:
            for event in obj.get_events(ModelEventAction(action)):
                self.event_helper.record(event)
