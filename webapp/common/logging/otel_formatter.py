"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import functools
import json
import logging
import string
import time
from typing import Any

from webapp.common.error_handling.exceptions import AppException
from webapp.common.json import DefaultJSONEncoder


class OtelFormatter(logging.Formatter):
    label_allowed_chars: str = f'{string.ascii_letters}{string.digits}_'
    log_level_mapping: dict[int, int] = {
        logging.DEBUG: 5,
        logging.INFO: 10,
        logging.WARNING: 15,
        logging.ERROR: 20,
        logging.CRITICAL: 25,
    }

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(self.build_payload(record), cls=DefaultJSONEncoder)

    @functools.lru_cache(256)  # noqa: B019
    def format_label(self, label: str) -> str | None:
        # The label uses way fewer characters then allowed, just a-z0-9_
        cleaned_label = ''.join(char for char in label if char in self.label_allowed_chars)
        if len(cleaned_label) == 0:
            return None
        return f'parkapi.{cleaned_label.lower()}'

    def build_tags(self, record: logging.LogRecord) -> dict[str, Any]:
        tags = {}

        extra_tags = getattr(record, 'tags', {})
        if not isinstance(extra_tags, dict):
            return tags

        for tag_name, tag_value in extra_tags.items():
            cleared_name = self.format_label(tag_name)
            if cleared_name is not None:
                tags[cleared_name] = tag_value

        return tags

    def build_payload(self, record: logging.LogRecord) -> dict:
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
            'Body': record.msg,
        }
