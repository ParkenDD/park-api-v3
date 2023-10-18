"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.error_handling.exceptions import AppException


class ObjectNotFoundException(AppException):
    """
    The requested object was not found or is out of scope.
    This exception may be extended (e.g. CustomerNotFoundException) for specific object types if needed.
    """

    code = 'not_found'
    http_status = 404
