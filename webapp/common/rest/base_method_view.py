"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import TYPE_CHECKING, Any, Optional

from flask import Response, jsonify
from flask.views import MethodView
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator, T_Dataclass
from validataclass_search_queries.pagination import (
    PaginatedResult,
    paginated_api_response,
)
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.common.config import ConfigHelper
from webapp.common.unset_parameter import UnsetParameter

from .exceptions import InputValidationException
from .request_helper import RequestHelper

if TYPE_CHECKING:
    from webapp.common.logging import Logger


class BaseMethodView(MethodView):
    """
    Base class derived from Flask's `MethodView` for rest API views.

    See also the specialized variants `ClientApiBaseMethodView` and `ServerApiBaseMethodView`.
    """

    # Dependencies
    logger: 'Logger'
    request_helper: RequestHelper
    config_helper: ConfigHelper

    def __init__(
        self,
        *,
        logger: 'Logger',
        request_helper: RequestHelper,
        config_helper: ConfigHelper,
    ):
        self.logger = logger
        self.request_helper = request_helper
        self.config_helper = config_helper

    def validate_query_args(self, validator: DataclassValidator[T_Dataclass]) -> T_Dataclass:
        """
        Gets the query arguments from the current request and validates them using a `DataclassValidator`.

        If the validator raises a `ValidationError`, it is caught and wrapped inside an `InputValidationException`.
        """
        try:
            raw_input = self.request_helper.get_query_args(skip_empty=True)
            return validator.validate(raw_input)
        except ValidationError as e:
            raise InputValidationException('Validation errors in query parameters.', data=e.to_dict()) from e

    def validate_request(
        self,
        validator: DataclassValidator[T_Dataclass],
        *,
        default: Any = UnsetParameter,
        context_args: Optional[dict] = None,
    ) -> T_Dataclass:
        """
        Gets the parsed JSON body from the current request and validates it using a `DataclassValidator`.

        If no valid JSON body is present in the request a `WrongContentTypeException` is raised, unless the `default`
        parameter is set, in which case the value of it will be used as input for the validator.

        Context arguments can be passed to the validator using the `context_args` parameter (as a dictionary).

        If the validator raises a `ValidationError`, it is caught and wrapped inside an `InputValidationException`.
        """
        if not context_args:
            context_args = {}

        try:
            raw_input = self.request_helper.get_parsed_json(default=default)
            return validator.validate(raw_input, **context_args)
        except ValidationError as e:
            raise InputValidationException('Validation errors in request body.', data=e.to_dict()) from e

    def jsonify_paginated_response(
        self,
        paginated_result: PaginatedResult[Any],
        search_query: Optional[BaseSearchQuery],
    ) -> Response:
        """
        Generate a jsonified response from (potentially) paginated data, containing the paginated results in "items",
        the total number of results pre-pagination in "total_count", and information on how to get the next page of
        results ("next_id" / "next_offset" for the next start parameter and "next_path" with full path and query
        parameters for the next page).

        If there is no next page, no "next_*" fields will be set. This is determined from the results, total count and
        pagination parameters. There is no next page if one of the following conditions is true:

        - The search query does not have any pagination parameters (i.e. no pagination is used).
        - The paginated result is empty.
        - The number of results on the current page is less than the page size (from the "limit" parameter).
        - For offset pagination only: The next offset would be greater than or equal to the total amount of results.

        When using cursor pagination, there are cases where the last page cannot be determined, namely if the last page
        is a full page. In that case, you will get a "next_id" that will result in an empty last page.
        """
        return jsonify(
            paginated_api_response(
                paginated_result,
                search_query,
                request_path=self.request_helper.get_path(),
                original_params=self.request_helper.get_query_args(skip_empty=True),
            )
        )
