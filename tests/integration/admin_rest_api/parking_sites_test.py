"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.testing import FlaskClient


def test_generate_duplicates_simple(
    multi_source_parking_site_test_data: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/generate',
        auth=('dev', 'test'),
        json={
            'radius': 25000,
        },
    )

    assert result.status_code == 200
    duplicates = result.json['items']

    # As we just output duplicates where each site is at another source, and we have three sources, we expect
    # two duplicates pairs, therefor four datasets
    assert len(duplicates) == 4


def test_generate_duplicates_source_uids(
    multi_source_parking_site_test_data: None,
    admin_api_test_client: FlaskClient,
) -> None:
    result = admin_api_test_client.post(
        '/api/admin/v1/parking-sites/duplicates/generate',
        auth=('dev', 'test'),
        json={
            'radius': 25000,
            'source_uids': ['source-1'],
        },
    )

    assert result.status_code == 200
    duplicates = result.json['items']

    # As we just output duplicates where each site is at another source, and we have three sources, filtered to one,
    # we expect two duplicates pairs, because the other pair is between source-2 and source-3
    assert len(duplicates) == 2
