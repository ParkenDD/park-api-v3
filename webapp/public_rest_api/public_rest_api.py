"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Response

from webapp.common.blueprint import Blueprint
from webapp.dependencies import dependencies

from .base_blueprint import PublicApiBaseBlueprint
from .datex2 import Datex2Blueprint
from .park_api_v1 import ParkApiV1Blueprint
from .park_api_v2 import ParkApiV2Blueprint
from .parking_sites import ParkingSiteBlueprint
from .parking_spots import ParkingSpotBlueprint
from .sources import SourceBlueprint
from .tiles import TilesBlueprint


class PublicRestApi(Blueprint):
    documentation_base = True

    blueprints_classes: list[type[PublicApiBaseBlueprint]] = [
        Datex2Blueprint,
        ParkApiV1Blueprint,
        ParkApiV2Blueprint,
        ParkingSpotBlueprint,
        ParkingSiteBlueprint,
        SourceBlueprint,
        TilesBlueprint,
    ]

    def __init__(self):
        super().__init__('public', __name__, url_prefix='/api/public')

        for blueprint_class in self.blueprints_classes:
            self.register_blueprint(blueprint_class())

        self.after_request(self.add_cors_header)

    @staticmethod
    def add_cors_header(response: Response) -> Response:
        if dependencies.get_config_helper().get('CORS_ALLOW_ALL'):
            response.headers['Access-Control-Allow-Origin'] = '*'
        return response
