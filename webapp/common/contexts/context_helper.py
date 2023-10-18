"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from flask.ctx import AppContext, RequestContext, has_request_context
from flask.globals import app_ctx, request_ctx


class ContextHelper:
    """
    Helper class for working with Flask application and request contexts.
    """

    @staticmethod
    def get_app_context() -> Optional[AppContext]:
        """
        Returns the current application context, or None if no application context exists.
        """
        return app_ctx

    @staticmethod
    def get_request_context() -> Optional[RequestContext]:
        """
        Returns the current request context, or None if no request context exists.
        """
        return request_ctx

    @staticmethod
    def has_request_context() -> bool:
        """
        Returns True if a request context exists on the request context stack, False otherwise.
        """
        return has_request_context()
