"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional


class AppException(Exception):
    """
    Base exception class for all errors thrown by the application. (See also: RestApiException)
    Each AppException has a "code", which is a string identifier like "auth_failed", an HTTP status code (e.g. 403)
    which should not be confused with the string "code", and a human-readable "message" that may contain more
    details to the error.
    Optionally the "data" attribute can be set, which can contain any type of data (e.g. dicts) with additional
    information on the error.
    Finally, the optional "debug" attribute can be set to any type of data. Contrary to the other attributes the
    "debug" attribute will ONLY be included in API responses when the application is in DEBUG mode, thus it may
    be filled with potentially sensitive and long data (like stack traces or object dumps).
    """

    code: str = 'unspecified_error'
    message: str = ''
    http_status: int = 500
    data: Any = None
    debug_data: Any = None

    def __init__(
        self,
        message: str,
        *,
        http_status: Optional[int] = None,
        code: Optional[str] = None,
        data: Any = None,
        debug: Any = None,
    ):
        self.message = message
        if http_status is not None:
            self.http_status = http_status
        if code is not None:
            self.code = code
        if data is not None:
            self.data = data
        if debug is not None:
            self.debug_data = debug

    def __str__(self):
        if self.message:
            return '{}: {} ({})'.format(self.code, self.message, self.http_status)

        return '{} ({})'.format(self.code, self.http_status)

    def response_data(self, debug_mode: bool = False):
        response_data = {
            'code': self.code,
            'message': self.message,
        }
        if self.data:
            response_data['data'] = self.data

        # Append debug data only when the application is in debug mode
        if debug_mode and self.debug_data:
            response_data['_debug'] = self.debug_data

        return response_data
