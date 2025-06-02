"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from flask.testing import FlaskClient
from flask_openapi.generator import generate_openapi
from openapi_core import OpenAPI
from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest, WerkzeugOpenAPIResponse
from werkzeug.test import TestResponse

from webapp.common.flask_app import App


class OpenApiFlaskClient(FlaskClient):
    openapi_realm: str | None = None

    def __init__(self, *args: Any, openapi_realm: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.openapi_realm = openapi_realm

    def open(self, *args: Any, **kwargs: Any) -> TestResponse:
        response = super().open(*args, **kwargs)

        if self.openapi_realm is None:
            return response

        openapi_dict = generate_openapi(self.openapi_realm)
        openapi_dict = self.no_additional_properties(openapi_dict)

        openapi = OpenAPI.from_dict(openapi_dict)

        openapi.validate_response(WerkzeugOpenAPIRequest(response.request), WerkzeugOpenAPIResponse(response))

        return response

    def no_additional_properties(self, data: Any):
        if isinstance(data, dict):
            # Patch in additionalProperties in case of an object field
            if data.get('type') == 'object' and 'additionalProperties' not in data.keys():
                data['additionalProperties'] = False

            return {key: self.no_additional_properties(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self.no_additional_properties(item) for item in data]

        return data


class OpenApiApp(App):
    """
    Flask application extended with OpenApiFlaskClient
    """

    test_client_class = OpenApiFlaskClient
