"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import make_response
from flask_openapi.decorator import Parameter, Response, ResponseData, document
from flask_openapi.schema import BooleanField, EnumField
from parkapi_sources.models.enums import PurposeType
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView

from .tiles_handler import RENDER_PARKING_SITES_MIN_ZOOM, TilesHandler
from .tiles_validators import TileFilterInput


class TilesBlueprint(PublicApiBaseBlueprint):
    documented: bool = True
    tiles_handler: TilesHandler

    def __init__(self):
        super().__init__('tiles', __name__, url_prefix='/v3/tiles')

        self.tiles_handler = TilesHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            generic_import_service=dependencies.get_generic_import_service(),
        )

        self.add_url_rule(
            '/<int:z>/<int:x>/<int:y>.mvt',
            view_func=TilesMethodView.as_view(
                'tiles',
                **self.get_base_method_view_dependencies(),
                tiles_handler=self.tiles_handler,
            ),
        )


class TilesMethodView(PublicApiBaseMethodView):
    tiles_handler: TilesHandler
    tile_filter_validator = DataclassValidator(TileFilterInput)

    def __init__(self, *, tiles_handler: TilesHandler, **kwargs):
        super().__init__(**kwargs)
        self.tiles_handler = tiles_handler

    @document(
        description='Generates a Mapbox Vector Tile with a layer `parking_sites`. Each feature contains the properties '
        '`id`, `name`, `purpose`, `capacity` (if known) and `free_capacity` (only if current realtime data is '
        f'available). Tiles with a zoom level below {RENDER_PARKING_SITES_MIN_ZOOM} contain an empty layer.',
        path=[
            Parameter('z', schema=int, example=12),
            Parameter('x', schema=int, example=2144),
            Parameter('y', schema=int, example=1408),
        ],
        query=[
            Parameter(
                'purpose',
                schema=EnumField(enum=PurposeType),
                description='If set, just ParkingSites with this purpose are shown.',
            ),
            Parameter(
                'ignore_duplicates',
                schema=BooleanField(),
                description='Defaults to true. If set to false, you will get ParkingSites flagged as duplicates, too.',
            ),
        ],
        response=[Response(ResponseData(mimetype='application/x-protobuf'), description='Tile in protobuf format.')],
    )
    def get(self, z: int, x: int, y: int):
        tile_filter_input = self.validate_query_args(self.tile_filter_validator)

        tile = self.tiles_handler.generate_tile(x, y, z, tile_filter_input)

        response = make_response(tile)
        response.headers['Content-Type'] = 'application/x-protobuf'
        return response
