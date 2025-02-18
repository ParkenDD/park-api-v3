"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import copy
import functools
import logging
import string
import time
from typing import Any

from requests import Session

from webapp.common.error_handling.exceptions import AppException

BasicAuth = tuple[str, str] | None


class OTelEmitter:
    success_response_code: int = 204
    logger_tag: str = 'logger'
    label_allowed_chars: str = f'{string.ascii_letters}{string.digits}_'

    log_level_mapping: dict[int, int] = {
        logging.DEBUG: 5,
        logging.INFO: 10,
        logging.WARNING: 15,
        logging.ERROR: 20,
        logging.CRITICAL: 25,
    }

    def __init__(self, url: str, tags: dict | None = None, auth: BasicAuth | None = None):
        self.tags = tags or {}
        self.url = url
        self.auth = auth

        self._session: Session | None = None

    def __call__(self, record: logging.LogRecord, line: str):
        payload = self.build_payload(record, line)
        resp = self.session.post(self.url, json=payload)
        if resp.status_code != self.success_response_code:
            raise ValueError('Unexpected OTel API response status code: {0}'.format(resp.status_code))

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session()
            self._session.auth = self.auth or None
        return self._session

    def close(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    @functools.lru_cache(256)  # noqa: B019
    def format_label(self, label: str) -> str | None:
        # The label uses way fewer characters then allowed, just a-z0-9_
        cleaned_label = ''.join(char for char in label if char in self.label_allowed_chars)
        if len(cleaned_label) == 0:
            return None
        return f'parkapi.{cleaned_label.lower()}'

    def build_tags(self, record: logging.LogRecord) -> dict[str, Any]:
        tags = copy.deepcopy(self.tags)
        tags[self.logger_tag] = record.name

        extra_tags = getattr(record, 'tags', {})
        if not isinstance(extra_tags, dict):
            return tags

        for tag_name, tag_value in extra_tags.items():
            cleared_name = self.format_label(tag_name)
            if cleared_name is not None:
                tags[cleared_name] = tag_value

        return tags

    def build_payload(self, record: logging.LogRecord, line: str) -> dict:
        ts = int(time.time() * 1e9)

        tracing_ids = getattr(record, 'tracing_ids', {})
        if tracing_ids.get('trace_id') is None or tracing_ids.get('span_id') is None:
            raise AppException('TraceID or SpanID is missing at log record.')

        return {
            'Timestamp': ts,
            'Attributes': {
                **self.build_tags(record),
            },
            'Resource': {
                'service.name': 'park_api',
            },
            'TraceId': tracing_ids['trace_id'],
            'SpanId': tracing_ids['span_id'],
            'SeverityText': 'WARN' if record.levelno == logging.WARNING else record.levelname,
            'SeverityNumber': self.log_level_mapping[record.levelno],
            'Body': line,
        }
