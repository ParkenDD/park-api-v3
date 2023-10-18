"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from flask import Request
from flask import request as flask_request

from .base_error_handler import BaseErrorHandler


class ErrorDispatcher:
    """
    Class that can be registered as the global error handler. Dispatches errors/exceptions to other error handlers
    (classes that implement BaseErrorHandler), depending on certain rules like request path prefixes.
    """

    rest_api_error_handler: BaseErrorHandler

    def __init__(self, rest_api_error_handler: BaseErrorHandler):
        # Initialize error handlers
        self.rest_api_error_handler = rest_api_error_handler

    def dispatch_error(self, error: Exception, request: Optional[Request] = None):
        """
        Decides which ErrorHandler class is responsible for this exception (by checking the prefix of the request path)
        and passes the exception to it.
        Returns the result of the error handler, which should be a tuple of an HTTP response and a response code.
        If the exception could not be handled (e.g. because no handler is registered), the exception is re-raised.
        """
        if request is None:  # pragma: no cover
            request = flask_request

        error_handler = self._get_error_handler_for(request)
        response = error_handler.handle_error(error)

        if response:
            return response
        raise error

    def _get_error_handler_for(self, request: Request) -> BaseErrorHandler:
        return self.rest_api_error_handler

    def wrap(self, func):
        """
        Decorator to wrap a function inside a try-except block that dispatches exceptions raised by the function.
        """

        def decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return self.dispatch_error(e)

        return decorator
