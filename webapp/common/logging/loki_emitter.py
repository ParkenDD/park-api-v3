"""
Copyright 2019 Andrey Maslov, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import copy
import functools
import logging
import string
import time
from typing import Any, Optional

import requests

BasicAuth = Optional[tuple[str, str]]


class LokiEmitter:
    """Base Loki emitter class."""

    success_response_code: int = 204
    level_tag: str = 'severity'
    logger_tag: str = 'logger'
    label_allowed_chars: str = ''.join((string.ascii_letters, string.digits, '_'))
    label_replace_with: tuple[tuple[str, str], ...] = (
        ("'", ''),
        ('"', ''),
        (' ', '_'),
        ('.', '_'),
        ('-', '_'),
    )
    session_class = requests.Session

    def __init__(self, url: str, tags: Optional[dict] = None, auth: Optional[BasicAuth] = None):
        """
        Create new Loki emitter.

        Arguments:
            url: Endpoint used to send log entries to Loki (e.g. `https://my-loki-instance/loki/api/v1/push`).
            tags: Default tags added to every log record.
            auth: Optional tuple with username and password for basic HTTP authentication.

        """
        #: Tags that will be added to all records handled by this handler.
        self.tags = tags or {}
        #: Loki JSON push endpoint (e.g `http://127.0.0.1/loki/api/v1/push`)
        self.url = url
        #: Optional tuple with username and password for basic authentication.
        self.auth = auth

        self._session: Optional[requests.Session] = None

    def __call__(self, record: logging.LogRecord, line: str):
        """Send log record to Loki."""
        payload = self.build_payload(record, line)
        resp = self.session.post(self.url, json=payload)
        if resp.status_code != self.success_response_code:
            raise ValueError('Unexpected Loki API response status code: {0}'.format(resp.status_code))

    @property
    def session(self) -> requests.Session:
        """Create HTTP session."""
        if self._session is None:
            self._session = self.session_class()
            self._session.auth = self.auth or None
        return self._session

    def close(self):
        """Close HTTP session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    @functools.lru_cache(256)  # noqa: B019
    def format_label(self, label: str) -> str:
        """
        Build label to match prometheus format.

        `Label format <https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels>`_
        """
        for char_from, char_to in self.label_replace_with:
            label = label.replace(char_from, char_to)
        return ''.join(char for char in label if char in self.label_allowed_chars)

    def build_tags(self, record: logging.LogRecord) -> dict[str, Any]:
        """Return tags that must be send to Loki with a log record."""
        tags = copy.deepcopy(self.tags)
        tags[self.level_tag] = record.levelname.lower()
        tags[self.logger_tag] = record.name

        extra_tags = getattr(record, 'tags', {})
        if not isinstance(extra_tags, dict):
            return tags

        for tag_name, tag_value in extra_tags.items():
            cleared_name = self.format_label(tag_name)
            if cleared_name:
                tags[cleared_name] = tag_value

        return tags

    def build_payload(self, record: logging.LogRecord, line) -> dict:
        """Build JSON payload with a log entry."""
        labels = self.build_tags(record)
        ns = 1e9
        ts = str(int(time.time() * ns))
        stream = {
            'stream': labels,
            'values': [[ts, line]],
        }
        return {'streams': [stream]}
