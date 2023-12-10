"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import os
from logging import Logger as PythonLogger
from typing import Optional

from webapp.common.config import ConfigHelper
from webapp.common.contexts import ContextHelper

from .local_file_handler import LocalFileHandler
from .loki_handler import LokiQueueHandler
from .models import LogMessageType, LogTag
from .stdout_handler import StdoutHandler


class Logger:
    config_helper: ConfigHelper
    context_helper: ContextHelper
    logger: PythonLogger
    local_file_handler: Optional[LocalFileHandler] = None
    stdout_handler: Optional[StdoutHandler] = None
    loki_handler: Optional[LokiQueueHandler] = None

    def __init__(self, config_helper: ConfigHelper, context_helper: ContextHelper):
        self.config_helper = config_helper
        self.context_helper = context_helper

        self.logger = logging.getLogger('app')
        self.logger.setLevel(logging.INFO)

        self.local_handler = LocalFileHandler(config_helper=config_helper)
        self.logger.addHandler(self.local_handler)

        if self.config_helper.get('LOKI_ENABLED'):
            self.loki_handler = LokiQueueHandler(config_helper=config_helper)
            self.logger.addHandler(self.loki_handler)

        if self.config_helper.get('STDOUT_LOGGING_ENABLED'):
            self.stdout_handler = StdoutHandler()
            self.logger.addHandler(self.stdout_handler)

    def set_tag(self, tag: LogTag, value: str):
        app_context = self.context_helper.get_app_context()
        if not hasattr(app_context, 'butterfly_log_tags'):
            app_context.butterfly_log_tags = {}
        app_context.butterfly_log_tags[tag] = value

    def _log(self, level: str, message_type: LogMessageType, message: str):
        app_context = self.context_helper.get_app_context()
        tags = {key.value: value for key, value in getattr(app_context, 'butterfly_log_tags', {}).items()}
        tags['type'] = message_type.value
        if os.environ.get('FLASK_RUN_FROM_CLI'):
            tags['initiator'] = 'cli'
        getattr(self.logger, level)(message, extra={'tags': tags})

    def debug(self, message_type: LogMessageType, message: str):
        self._log('debug', message_type, message)

    def info(self, message_type: LogMessageType, message: str):
        self._log('info', message_type, message)

    def warning(self, message_type: LogMessageType, message: str):
        self._log('warning', message_type, message)

    def error(self, message_type: LogMessageType, message: str):
        self._log('error', message_type, message)

    def exception(self, message_type: LogMessageType, message: str):
        self._log('exception', message_type, message)

    def critical(self, message_type: LogMessageType, message: str):
        self._log('debug', message_type, message)

    def teardown_appcontext(self):
        if self.config_helper.get('LOKI_ENABLED'):
            self.loki_handler.teardown_appcontext()
