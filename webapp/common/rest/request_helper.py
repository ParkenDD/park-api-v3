"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Dict, Optional

from flask import Request
from flask import request as flask_request

from webapp.common.unset_parameter import UnsetParameter

from .exceptions import WrongContentTypeException


class RequestHelper:
    """
    Helper class that wraps the Flask request object.
    """

    request: Request

    def __init__(self, request: Optional[Request] = None):
        self.request = request if request else flask_request

    def get_parsed_json(self, *, default: Any = UnsetParameter) -> Any:
        """
        Returns the parsed JSON body of the current request.

        Raises a `WrongContentTypeException` if no JSON body is present, unless the `default` parameter is set, in which
        case the value of it is returned instead.
        """
        # Don't raise a "Failed to decode JSON object" BadRequest exception if the request body is empty
        parsed_json = self.request.get_json() if self.request.content_length else None

        if parsed_json is None and default is UnsetParameter:
            raise WrongContentTypeException('Request must have Content-Type application/json and a valid JSON body.')

        return parsed_json if parsed_json is not None else default

    def get_query_args(self, skip_empty: bool = False) -> Dict[str, str]:
        """
        Returns a dictionary containing all query arguments of the request as strings. If `skip_empty` is True, empty
        parameters (i.e. empty strings) will be removed from the dictionary.

        For example, the query string `?foo=abc&bar=&baz=42` results in `{'foo': 'abc', 'bar': '', 'baz': '42'}` by
        default, or in `{'foo': 'abc', 'baz': '42'}` if `skip_empty` is True.
        """
        args = dict(self.request.args)
        if skip_empty:
            args = {key: value for key, value in args.items() if value is not None and value != ''}
        return args

    def get_path(self) -> str:
        return self.request.path

    def get_method(self) -> str:
        return self.request.method

    def get_headers(self) -> dict:
        return dict(self.request.headers)

    def get_client_ip(self):
        return self.request.headers.get('X-Forwarded-For', None)

    def get_origin(self) -> str:
        return self.request.environ.get('HTTP_ORIGIN')

    def get_request_body(self) -> bytes:
        return self.request.get_data()

    def get_request_body_text(self) -> str:
        return self.request.get_data(as_text=True)

    def get_basicauth_username(self) -> Optional[str]:
        if not self.request.authorization:
            return None

        return self.request.authorization.username
