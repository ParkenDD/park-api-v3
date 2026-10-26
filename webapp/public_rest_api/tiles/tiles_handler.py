"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timedelta, timezone

import mercantile
import numpy as np
import shapely
from mapbox_vector_tile import encode
from parkapi_sources.models.enums import ParkingSiteType

from webapp.common.sqlalchemy.geometry import geojson_to_shape
from webapp.public_rest_api.base_handler import PublicApiBaseHandler
from webapp.public_rest_api.tiles.tiles_validators import TileFilterInput
from webapp.repositories import ParkingSiteRepository
from webapp.repositories.parking_site_repository import ParkingSiteTileItem
from webapp.services.import_service import GenericImportService

RENDER_PARKING_SITES_MIN_ZOOM = 8
# Shapes are just a few pixels in size at lower zoom levels, so they are not worth the tile size there
RENDER_PARKING_SITE_GEOMETRIES_MIN_ZOOM = 12
TILE_EXTENT = 4096
# Shapes are clipped with some buffer around the tile, so that there are no visible edges at tile borders
TILE_BUFFER = 64
# Web Mercator is not defined for the poles
MAX_LATITUDE = 85.0511287798


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
        point_layer = {
            'name': 'parking_sites',
            'features': [],
        }
        geometry_layer = {
            'name': 'parking_site_geometries',
            'features': [],
        }

        # Don't render any parking sites if zoomed out too far
        if z < RENDER_PARKING_SITES_MIN_ZOOM:
            return encode(layers=[point_layer, geometry_layer])

        bbox = mercantile.bounds((x, y, z))
        filters = {
            'purpose': tile_filter_input.purpose,
            'types': tile_filter_input.types,
            'source_uids': tile_filter_input.source_uids,
            'ignore_duplicates': tile_filter_input.ignore_duplicates,
        }
        if tile_filter_input.hide_on_street_until_zoom is not None and z <= tile_filter_input.hide_on_street_until_zoom:
            filters['exclude_types'] = [ParkingSiteType.ON_STREET]

        # Parking sites with their geojson shape intersecting the tile's bounding box. As the shapes can be larger than
        # the tile, they are clipped to the tile plus a buffer.
        if z >= RENDER_PARKING_SITE_GEOMETRIES_MIN_ZOOM:
            for item in self.parking_site_repository.fetch_parking_site_tile_items_by_bounds(
                bbox,
                with_geojson=True,
                **filters,
            ):
                geometry = geojson_to_shape(item.geojson)
                if geometry is None:
                    continue
                geometry = shapely.transform(geometry, lambda c: self._to_tile_coordinates(c, x, y, z))
                geometry = shapely.clip_by_rect(
                    geometry,
                    -TILE_BUFFER,
                    -TILE_BUFFER,
                    TILE_EXTENT + TILE_BUFFER,
                    TILE_EXTENT + TILE_BUFFER,
                )
                # Clipping can result in empty geometries or geometry collections, which can't be encoded
                if geometry.is_empty or geometry.geom_type == 'GeometryCollection':
                    continue

                geometry_layer['features'].append({
                    'geometry': geometry,
                    'properties': self._get_properties(item),
                })

        # Parking sites whose shape is part of this tile are flagged in the point layer, so that clients can show the
        # shape instead of the point, but still have a single point per parking site e.g. for labels.
        ids_with_geometry = {feature['properties']['id'] for feature in geometry_layer['features']}

        # Parking sites with their point in the tile's bounding box
        for item in self.parking_site_repository.fetch_parking_site_tile_items_by_bounds(bbox, **filters):
            point = shapely.transform(
                shapely.Point(item.lon, item.lat), lambda c: self._to_tile_coordinates(c, x, y, z)
            )
            properties = self._get_properties(item)
            if item.id in ids_with_geometry:
                properties['has_geometry'] = True
            point_layer['features'].append({
                'geometry': point,
                'properties': properties,
            })

        return encode(layers=[point_layer, geometry_layer], default_options={'y_coord_down': True})

    @staticmethod
    def _to_tile_coordinates(coordinates: np.ndarray, x: int, y: int, z: int) -> np.ndarray:
        """
        Projects WGS84 lon / lat coordinates to Web Mercator tile coordinates of the given tile, with y pointing down.
        """
        lon = coordinates[:, 0]
        lat = np.radians(np.clip(coordinates[:, 1], -MAX_LATITUDE, MAX_LATITUDE))
        scale = 2**z

        tile_x = ((lon + 180) / 360 * scale - x) * TILE_EXTENT
        tile_y = ((1 - np.log(np.tan(lat) + 1 / np.cos(lat)) / np.pi) / 2 * scale - y) * TILE_EXTENT

        return np.column_stack([tile_x, tile_y])

    def _get_properties(self, item: ParkingSiteTileItem) -> dict:
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

        return properties

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
