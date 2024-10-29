"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.error_handling.exceptions import AppException


class RestApiException(AppException):
    """
    Base exception class for errors that are specific to REST APIs.
    """


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


class InvalidInputException(RestApiException):
    code = 'invalid_input'
    http_status = 400
