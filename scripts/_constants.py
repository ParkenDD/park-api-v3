"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

DATA_TYPES: dict[str, tuple[str, str]] = {
    'xlsx': ('xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'csv': ('csv', 'text/csv'),
    'xml': ('xml', 'application/xml'),
    'json': ('json', 'application/json'),
    'geojson': ('json', 'application/json'),
}

DEFAULT_BASE_URL = 'https://api.mobidata-bw.de/park-api'
PUSH_BASE_PATH = '/api/admin/v1/generic'
DUPLICATES_BASE_PATH = '/api/admin/v1/parking-sites/duplicates'
USER_AGENT = 'ParkAPIv3 Push Client v1.0.0'
