"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.schema import DateTimeField, JsonSchema, StringField, UriField

source_schema = JsonSchema(
    title='Source',
    properties={
        'uid': StringField(minLength=1, maxLength=256),
        'name': StringField(maxLength=256, required=False),
        'public_url': UriField(maxLength=4096),
        'last_import': DateTimeField(required=False),
        'attribution_license': StringField(required=False),
        'attribution_contributor': StringField(maxLength=256, required=False),
        'attribution_url': StringField(maxLength=256, required=False),
    },
)


source_example = {}
