"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.blueprint import Blueprint

from .base_blueprint import AdminApiBaseBlueprint
from .generic_parking_sites import GenericParkingSitesBlueprint


class AdminRestApi(Blueprint):
    documentation_base = True
    documentation_auth = 'basic'

    blueprints_classes: list[type[AdminApiBaseBlueprint]] = [
        GenericParkingSitesBlueprint,
    ]

    def __init__(self):
        super().__init__('admin', __name__, url_prefix='/api/admin/v1')

        for blueprint_class in self.blueprints_classes:
            self.register_blueprint(blueprint_class())
