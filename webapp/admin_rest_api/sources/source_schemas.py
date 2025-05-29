"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Request
from flask_openapi.schema import BooleanField, JsonSchema, StringField, UriField

source_request_schema = JsonSchema(
    title='Source Request',
    properties={
        'uid': StringField(minLength=1, maxLength=256),
        'name': StringField(minLength=256),
        'has_realtime_data': BooleanField(),
        'timezone': StringField(required=False, default='Europe/Berlin'),
        'public_url': UriField(required=False),
        'attribution_license': StringField(required=False),
        'attribution_url': StringField(required=False),
        'attribution_contributor': StringField(required=False),
    },
)

source_request_example = {
    'uid': 'demo-source',
    'name': 'Demo Source',
    'has_realtime_data': True,
    'timezone': 'Europe/Berlin',
    'public_url': 'https://demo.source.com',
    'attribution_license': 'CC BY-SA 4.0',
    'attribution_url': 'https://demo.source.com/attribution',
    'attribution_contributor': 'Demo Contributor',
}


source_request = Request(source_request_schema, source_request_example)
