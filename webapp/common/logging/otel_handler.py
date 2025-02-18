"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import os
from logging import Handler, LogRecord
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue

from webapp.common.config import ConfigHelper

from .otel_emitter import BasicAuth, OTelEmitter


class OTelHandler(Handler):
    def __init__(self, url: str, tags: dict | None = None, auth: BasicAuth | None = None):
        super().__init__()
        self.emitter = OTelEmitter(url, tags, auth)

    def handleError(self, record: LogRecord):  # noqa: N802
        self.emitter.close()
        super().handleError(record)

    def emit(self, record: LogRecord):
        try:
            self.emitter(record, self.format(record))
        except Exception:
            self.handleError(record)


class OTelQueueHandler(QueueHandler):
    queue: Queue
    listener: QueueListener
    handler: OTelHandler

    def __init__(self, config_helper: ConfigHelper):
        if not config_helper.get('OTEL_ENABLED'):
            return

        self.queue = Queue()
        super().__init__(self.queue)
        self.setLevel(logging.INFO)

        if config_helper.get('OTEL_USER') and config_helper.get('OTEL_PASSWORD'):
            auth = BasicAuth(config_helper.get('OTEL_USER'), config_helper.get('OTEL_PASSWORD'))
        else:
            auth = None

        self.handler = OTelHandler(
            url=config_helper.get('OTEL_URL'),
            tags=config_helper.get('OTEL_TAGS'),
            auth=auth,
        )
        self.listener = QueueListener(self.queue, self.handler)
        self.listener.start()

    def teardown_appcontext(self):
        if os.environ.get('FLASK_RUN_FROM_CLI'):
            self.listener.enqueue_sentinel()
            self.listener.stop()
