"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from sqlalchemy import func, select

from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.models import ParkingSite


class ParkingSiteModelTest:
    @staticmethod
    def test_delete_parking_site_referenced_as_duplicate_unsets_reference(db: SQLAlchemy) -> None:
        source = get_source()
        canonical = get_parking_site(source=source, original_uid='canonical')
        duplicate = get_parking_site(source=source, original_uid='duplicate')
        db.session.add(canonical)
        db.session.add(duplicate)
        db.session.flush()

        duplicate.duplicate_of_parking_site_id = canonical.id
        db.session.commit()

        db.session.delete(canonical)
        db.session.commit()

        remaining = db.session.get(ParkingSite, duplicate.id)
        assert remaining is not None
        assert remaining.duplicate_of_parking_site_id is None

    @staticmethod
    def test_geojson_geometry_follows_geojson(db: SQLAlchemy) -> None:
        parking_site = get_parking_site(source=get_source())
        parking_site.geojson = {'type': 'LineString', 'coordinates': [[10.0, 50.0], [10.1, 50.0]]}
        db.session.add(parking_site)
        db.session.commit()

        def get_geojson_geometry_wkt() -> str | None:
            return db.session.execute(
                select(func.ST_AsText(ParkingSite.geojson_geometry)).where(ParkingSite.id == parking_site.id),
            ).scalar_one()

        assert get_geojson_geometry_wkt() == 'LINESTRING(10 50,10.1 50)'

        parking_site.geojson = {'type': 'Polygon', 'coordinates': 'broken'}
        db.session.commit()

        assert get_geojson_geometry_wkt() is None

        parking_site.geojson = {'type': 'LineString', 'coordinates': [[10.0, 50.0], [10.2, 50.0]]}
        db.session.commit()
        parking_site.geojson = None
        db.session.commit()

        assert get_geojson_geometry_wkt() is None
