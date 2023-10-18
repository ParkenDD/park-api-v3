"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.error_handling.exceptions import AppException


class RestApiException(AppException):
    """
    Base exception class for errors that are specific to REST APIs.
    """

    pass


class RestApiRemoteException(RestApiException):
    code = 'remote_exception'
    http_status = 500


class RestApiNotImplementedException(RestApiException):
    code = 'not_implemented'
    http_status = 501


class WrongContentTypeException(RestApiException):
    code = 'wrong_content_type'
    http_status = 400


class WrongJsonTypeException(RestApiException):
    code = 'wrong_json_type'
    http_status = 400


class InputValidationException(RestApiException):
    code = 'validation_error'
    http_status = 400


class UnauthorizedException(RestApiException):
    code = 'unauthorized'
    http_status = 401


class PatchWithoutChangesException(RestApiException):
    """
    The client sent a PATCH request with no data to be changed in the resource.

    This happens either if the request body is a completely empty dictionary, or a non-empty dictionary that only contains fields not
    recognized (and thus discarded) by the input validation (e.g. `{'foo': 123}` will be treated exactly like `{}` if the field "foo"
    is not a defined field.

    The latter can also happen due to user permissions in some cases (e.g. a different validataclass is used for limited operators,
    where certain fields from the regular validataclass don't exist).
    """

    code = 'no_changes'
    http_status = 400


class ResourceInUseException(RestApiException):
    """
    The client tried to delete a resource that cannot be deleted currently because it is still in use (e.g. a pricegroup that is still
    assigned to a unit).
    """

    code = 'resource_in_use'
    http_status = 409


class InvalidChildException(RestApiException):
    """
    The client referenced a resource in the context of a parent resource, but the referenced resource is not actually
    a child of that parent resource.

    For example, when patching a charge station, the connectors of that station can be patched in the same request.
    This exception would be raised when the connectors do exist, but belong to a different station.
    """

    code = 'invalid_child'
    http_status = 400
