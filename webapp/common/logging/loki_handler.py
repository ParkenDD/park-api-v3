"""
Copyright 2019 Andrey Maslov, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import os
from logging import Handler, LogRecord
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue
from typing import Optional

from webapp.common.config import ConfigHelper

from .loki_emitter import BasicAuth, LokiEmitter


class LokiHandler(Handler):
    """
    Log handler that sends log records to Loki.

    `Loki API <https://github.com/grafana/loki/blob/master/docs/api.md>`_
    """

    def __init__(self, url: str, tags: Optional[dict] = None, auth: Optional[BasicAuth] = None):
        """
        Create new Loki logging handler.

        Arguments:
            url: Endpoint used to send log entries to Loki (e.g. `https://my-loki-instance/loki/api/v1/push`).
            tags: Default tags added to every log record.
            auth: Optional tuple with username and password for basic HTTP authentication.
        """
        super().__init__()
        self.emitter = LokiEmitter(url, tags, auth)

    def handleError(self, record: LogRecord):  # noqa: N802
        """Close emitter and let default handler take actions on error."""
        self.emitter.close()
        super().handleError(record)

    def emit(self, record: LogRecord):
        """Send log record to Loki."""
        try:
            self.emitter(record, self.format(record))
        except Exception:
            self.handleError(record)


class LokiQueueHandler(QueueHandler):
    """This handler automatically creates listener and `LokiHandler` to handle logs queue."""

    queue: Queue
    listener: QueueListener
    handler: LokiHandler

    def __init__(self, config_helper: ConfigHelper):
        """Create new logger handler with the specified queue and kwargs for the `LokiHandler`."""
        if not config_helper.get('LOKI_ENABLED'):
            return

        self.queue = Queue()
        super().__init__(self.queue)
        self.setLevel(logging.INFO)

        if config_helper.get('LOKI_USER') and config_helper.get('LOKI_PASSWORD'):
            auth = BasicAuth(config_helper.get('LOKI_USER'), config_helper.get('LOKI_PASSWORD'))
        else:
            auth = None

        self.handler = LokiHandler(
            url=config_helper.get('LOKI_URL'),
            tags=config_helper.get('LOKI_TAGS'),
            auth=auth,
        )
        self.listener = QueueListener(self.queue, self.handler)
        self.listener.start()

    def teardown_appcontext(self):
        # if flask cli commands are used, ensure that all events are sent
        if os.environ.get('FLASK_RUN_FROM_CLI'):
            self.listener.enqueue_sentinel()
            self.listener.stop()
