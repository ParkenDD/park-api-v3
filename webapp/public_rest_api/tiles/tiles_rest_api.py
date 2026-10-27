"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import make_response
from flask_openapi.decorator import Parameter, Response, ResponseData, document
from flask_openapi.schema import ArrayField, BooleanField, EnumField, IntegerField, StringField
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView

from .tiles_handler import RENDER_PARKING_SITE_GEOMETRIES_MIN_ZOOM, RENDER_PARKING_SITES_MIN_ZOOM, TilesHandler
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
        description='Generates a Mapbox Vector Tile with two layers. Layer `parking_sites` contains a point for each '
        'parking site. Layer `parking_site_geometries` contains the actual shape (polygon or line) of each parking site '
        'where it is known, clipped to the tile. Features in both layers contain the properties `id`, `name`, '
        '`purpose`, `type` (if known), `capacity` (if known) and `free_capacity` (only if current realtime data is '
        f'available). Tiles with a zoom level below {RENDER_PARKING_SITES_MIN_ZOOM} contain empty layers, tiles with a '
        f'zoom level below {RENDER_PARKING_SITE_GEOMETRIES_MIN_ZOOM} contain an empty `parking_site_geometries` layer. '
        'Points of parking sites whose shape is part of the same tile have the additional property `has_geometry` set to '
        'true, so that clients can show the shape instead of the point.',
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
                'types',
                schema=ArrayField(items=EnumField(enum=ParkingSiteType)),
                description='Comma-separated list of ParkingSite types. If set, just ParkingSites with one of these types '
                'are shown.',
                example='CAR_PARK,UNDERGROUND',
            ),
            Parameter(
                'source_uids',
                schema=ArrayField(items=StringField()),
                description='Comma-separated list of source UIDs. If set, just ParkingSites of these sources are shown.',
                example='source-uid-1,source-uid-2',
            ),
            Parameter(
                'ignore_duplicates',
                schema=BooleanField(),
                description='Defaults to true. If set to false, you will get ParkingSites flagged as duplicates, too.',
            ),
            Parameter(
                'hide_on_street_until_zoom',
                schema=IntegerField(minimum=0),
                description='If set, ParkingSites with type ON_STREET are hidden in tiles with a zoom level lower than or '
                'equal to this value.',
                example=12,
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
