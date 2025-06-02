"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Schema
from flask_openapi.schema import DateTimeField, EnumField, IntegerField, JsonSchema, StringField, UriField

from webapp.models.source import SourceStatus

source_schema = JsonSchema(
    title='Source',
    properties={
        'id': IntegerField(),
        'created_at': DateTimeField(),
        'modified_at': DateTimeField(),
        'uid': StringField(minLength=1, maxLength=256),
        'name': StringField(maxLength=256, required=False),
        'public_url': UriField(maxLength=4096),
        'last_import': DateTimeField(required=False),
        'attribution_license': StringField(required=False),
        'attribution_contributor': StringField(maxLength=256, required=False),
        'attribution_url': StringField(maxLength=256, required=False),
        'static_data_updated_at': DateTimeField(required=False),
        'realtime_data_updated_at': DateTimeField(required=False),
        'static_status': EnumField(enum=SourceStatus, required=False),
        'realtime_status': EnumField(enum=SourceStatus, required=False),
        'static_parking_site_error_count': IntegerField(required=False),
        'realtime_parking_site_error_count': IntegerField(required=False),
    },
)

source_example = {
    'uid': 'demo-source',
    'name': 'Demo Source',
    'public_url': 'https://demo.source.com',
    'attribution_license': 'CC BY-SA 4.0',
    'attribution_contributor': 'Demo Contributor',
    'attribution_url': 'https://demo.source.com/attribution',
    'static_status': 'PROVISIONED',
    'realtime_status': 'PROVISIONED',
    'id': 4,
    'created_at': '2025-05-29T08:11:16Z',
    'modified_at': '2025-05-29T08:11:16Z',
}


source_component = Schema('Source', source_schema, source_example)
