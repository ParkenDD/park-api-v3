"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timedelta, timezone

import mercantile
from mapbox_vector_tile import encode

from webapp.public_rest_api.base_handler import PublicApiBaseHandler
from webapp.public_rest_api.tiles.tiles_validators import TileFilterInput
from webapp.repositories import ParkingSiteRepository
from webapp.repositories.parking_site_repository import ParkingSiteTileItem
from webapp.services.import_service import GenericImportService

RENDER_PARKING_SITES_MIN_ZOOM = 8
TILE_EXTENT = 4096


class TilesHandler(PublicApiBaseHandler):
    parking_site_repository: ParkingSiteRepository
    generic_import_service: GenericImportService

    def __init__(
        self,
        *args,
        parking_site_repository: ParkingSiteRepository,
        generic_import_service: GenericImportService,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parking_site_repository = parking_site_repository
        self.generic_import_service = generic_import_service

    def generate_tile(self, x: int, y: int, z: int, tile_filter_input: TileFilterInput) -> bytes:
        layer = {
            'name': 'parking_sites',
            'features': [],
        }

        # Don't render any parking sites if zoomed out too far
        if z < RENDER_PARKING_SITES_MIN_ZOOM:
            return encode(layers=[layer])

        # Fetch parking sites in the tile's bounding box
        bbox = mercantile.bounds((x, y, z))
        parking_sites = self.parking_site_repository.fetch_parking_site_tile_items_by_bounds(
            bbox,
            purpose=tile_filter_input.purpose,
            types=tile_filter_input.types,
            source_uids=tile_filter_input.source_uids,
            ignore_duplicates=tile_filter_input.ignore_duplicates,
        )

        for item in parking_sites:
            point_x = int(TILE_EXTENT * (item.lon - bbox.west) / (bbox.east - bbox.west))
            point_y = int(TILE_EXTENT * (bbox.north - item.lat) / (bbox.north - bbox.south))

            properties = {
                'id': item.id,
                'name': item.name,
                'purpose': item.purpose.value,
            }
            if item.type is not None:
                properties['type'] = item.type.value
            if item.capacity is not None:
                properties['capacity'] = item.capacity
            if item.realtime_free_capacity is not None and self._has_current_realtime_data(item):
                properties['free_capacity'] = item.realtime_free_capacity

            layer['features'].append({
                'geometry': f'POINT({point_x} {point_y})',
                'properties': properties,
            })

        return encode(layers=[layer], default_options={'y_coord_down': True})

    def _has_current_realtime_data(self, item: ParkingSiteTileItem) -> bool:
        if not item.has_realtime_data or item.realtime_data_updated_at is None:
            return False

        # Realtime data of pull sources is outdated after 30 minutes, realtime data of push sources after 24 hours
        if self.generic_import_service.is_pull_source(item.source_uid):
            outdated_after_minutes = self.config_helper.get('UNSET_REALTIME_PULL_AFTER_MINUTES')
        else:
            outdated_after_minutes = self.config_helper.get('UNSET_REALTIME_PUSH_AFTER_MINUTES')

        return item.realtime_data_updated_at >= datetime.now(tz=timezone.utc) - timedelta(
            minutes=outdated_after_minutes,
        )
