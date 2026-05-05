"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

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
