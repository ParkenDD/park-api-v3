"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import string

from requests import Session

from webapp.common.logging.otel_formatter import OtelFormatter

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
        self.formatter = OtelFormatter()

    def __call__(self, record: logging.LogRecord):
        payload = self.formatter.format(record)

        resp = self.session.post(self.url, data=payload)
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
