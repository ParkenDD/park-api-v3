"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from logging import NOTSET, Handler, LogRecord

from requests import Session


class HttpPostJsonHandler(Handler):
    url: str
    credentials: tuple[str, str] | None = None
    _session: Session | None = None

    def __init__(self, url: str, *, level: int = NOTSET, credentials: tuple[str, str] | None = None):
        super().__init__(level=level)

        self.url = url
        self.credentials = credentials

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session()
            self._session.auth = self.credentials

        return self._session

    def emit(self, record: LogRecord):
        data = self.format(record)

        self.session.post(self.url, data=data, headers={'Content-Type': 'application/json'})

    def close(self):
        if self._session is None:
            return

        self._session.close()
        self._session = None
