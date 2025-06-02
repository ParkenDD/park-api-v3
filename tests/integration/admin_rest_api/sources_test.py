"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from http import HTTPStatus
from unittest.mock import ANY

from flask.testing import FlaskClient

from tests.integration.admin_rest_api.helpers import load_admin_client_request_input


def test_create_source(admin_api_test_client: FlaskClient) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/sources',
        auth=('source', 'test'),
        json=load_admin_client_request_input('source'),
    )

    assert result.status_code == HTTPStatus.CREATED
    assert result.json == SOURCE_RESPONSE


def test_update_source(
    rest_enabled_source: None,
    admin_api_test_client: FlaskClient,
) -> None:
    source_data = load_admin_client_request_input('source')
    source_data['name'] = 'Updated Source'
    result = admin_api_test_client.post(
        '/api/admin/v1/sources',
        auth=('source', 'test'),
        json=source_data,
    )

    assert result.status_code == HTTPStatus.OK
    expected_response = deepcopy(SOURCE_RESPONSE)
    expected_response['name'] = 'Updated Source'
    assert result.json == expected_response


SOURCE_RESPONSE = {
    'uid': 'source',
    'name': 'Demo Source',
    'public_url': 'https://demo.source.com',
    'attribution_license': 'CC BY-SA 4.0',
    'attribution_contributor': 'Demo Contributor',
    'attribution_url': 'https://demo.source.com/attribution',
    'static_status': 'PROVISIONED',
    'realtime_status': 'PROVISIONED',
    'id': 1,
    'created_at': ANY,
    'modified_at': ANY,
}
