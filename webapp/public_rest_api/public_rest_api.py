"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.blueprint import Blueprint

from .base_blueprint import PublicApiBaseBlueprint
from .datex2 import Datex2Blueprint
from .park_api_v1 import ParkApiV1Blueprint
from .park_api_v2 import ParkApiV2Blueprint
from .parking_sites import ParkingSiteBlueprint
from .parking_spots import ParkingSpotBlueprint
from .sources import SourceBlueprint


class PublicRestApi(Blueprint):
    documentation_base = True

    blueprints_classes: list[type[PublicApiBaseBlueprint]] = [
        Datex2Blueprint,
        ParkApiV1Blueprint,
        ParkApiV2Blueprint,
        ParkingSpotBlueprint,
        ParkingSiteBlueprint,
        SourceBlueprint,
    ]

    def __init__(self):
        super().__init__('public', __name__, url_prefix='/api/public')

        for blueprint_class in self.blueprints_classes:
            self.register_blueprint(blueprint_class())
