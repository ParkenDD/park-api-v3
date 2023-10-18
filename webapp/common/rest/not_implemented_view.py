"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import request
from flask.views import View

from webapp.common.rest.exceptions import RestApiNotImplementedException


class NotImplementedView(View):
    """
    Raises a RestApiNotImplementedException for all methods.
    """

    def dispatch_request(self, *args, **kwargs):
        raise RestApiNotImplementedException('{} method not implemented yet.'.format(request.method.upper()))
