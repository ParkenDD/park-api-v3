"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.decorator import Schema
from flask_openapi.schema import JsonSchema

from webapp.shared.parking_site.parking_sites_schema import parking_site_base_properties

parking_site_history_schema = JsonSchema(
    title='ParkingSiteHistory',
    properties=parking_site_base_properties,
)

parking_site_history_example = {}

parking_site_history_component = Schema(
    'ParkingSiteHistory', schema=parking_site_history_schema, example=parking_site_history_example
)
