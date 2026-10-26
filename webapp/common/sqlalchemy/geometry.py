"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import shapely
from shapely.errors import GEOSException
from shapely.geometry import shape
from sqlalchemy import func
from sqlalchemy.sql.type_api import UserDefinedType

from webapp.extensions import db


class Geometry(UserDefinedType):
    """
    Generic geometry column, which can hold any geometry type in contrast to Point.
    """

    cache_ok = True

    def get_col_spec(self, **kwargs) -> str:
        engine_name = db.session.get_bind().dialect.name
        if engine_name in ('postgresql', 'mysql'):
            return 'GEOMETRY'

        raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')


def geojson_to_shape(geojson: dict | None) -> shapely.Geometry | None:
    """
    Converts a GeoJSON geometry to a shapely geometry. Returns None for missing, empty or broken geometries, because
    source data is not always valid.
    """
    if not geojson:
        return None
    try:
        geometry = shape(geojson)
    except (AttributeError, KeyError, TypeError, ValueError, GEOSException):
        return None
    if geometry.is_empty:
        return None
    return geometry


def geojson_to_sql_geometry(geojson: dict | None):
    geometry = geojson_to_shape(geojson)
    if geometry is None:
        return None

    engine_name = db.session.get_bind().dialect.name
    if engine_name == 'postgresql':
        return func.ST_GeomFromText(geometry.wkt, 4326)
    if engine_name == 'mysql':
        return func.ST_GeomFromText(geometry.wkt, 4326, 'axis-order=long-lat')

    raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')
