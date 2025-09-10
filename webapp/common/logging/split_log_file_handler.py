"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from logging import Formatter, Handler, LogRecord
from logging.handlers import WatchedFileHandler
from pathlib import Path

from webapp.common.logging.models import LogMessageType


class SplitLogFileHandler(Handler):
    _file_handlers: dict[LogMessageType, WatchedFileHandler] = {}

    def __init__(self, log_path: str, **kwargs):
        super().__init__()
        for log_type in LogMessageType:
            log_name = log_type.value.lower().replace('_', '-')
            self._file_handlers[log_type] = WatchedFileHandler(
                filename=Path(log_path, f'{log_name}.log'),
                **kwargs,
            )

    def emit(self, record: LogRecord):
        log_type: LogMessageType = getattr(record, 'attributes', {}).get('type', LogMessageType.MISC)
        self._file_handlers[log_type].emit(record)

    def close(self):
        for handler in self._file_handlers.values():
            handler.close()

    def setFormatter(self, formatter: Formatter):
        for handler in self._file_handlers.values():
            handler.setFormatter(formatter)

    def createLock(self):
        for handler in self._file_handlers.values():
            handler.createLock()

    def set_name(self, name: str):
        for handler in self._file_handlers.values():
            handler.set_name(name)

    def acquire(self):
        for handler in self._file_handlers.values():
            handler.acquire()

    def release(self):
        for handler in self._file_handlers.values():
            handler.release()

    def setLevel(self, level: int):
        for handler in self._file_handlers.values():
            handler.setLevel(level)

    def flush(self):
        for handler in self._file_handlers.values():
            handler.flush()
