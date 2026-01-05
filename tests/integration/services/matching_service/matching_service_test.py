"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from webapp.common.sqlalchemy import SQLAlchemy
from webapp.dependencies import dependencies
from webapp.models import ParkingSite
from webapp.services.matching_service import MatchingService


@pytest.fixture
def matching_service() -> MatchingService:
    return dependencies.get_matching_service()


class MatchingServiceTest:
    @staticmethod
    def test_generate_duplicates_simple(
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        duplicates = matching_service.generate_duplicates(
            existing_matches=[],
            match_radius=25000,
        )
        # As we just output duplicates where each site is at another source. and we have three sources, we expect
        # two duplicates pairs, therefor four datasets
        assert len(duplicates) == 4

    @staticmethod
    def test_generate_duplicates_existing_duplicates(
        db: SQLAlchemy,
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        duplicate_site = db.session.get(ParkingSite, 3)
        duplicate_site.duplicate_of_parking_site_id = 4
        db.session.add(duplicate_site)
        db.session.commit()

        duplicates = matching_service.generate_duplicates(
            existing_matches=[],
            match_radius=25000,
        )
        # Even if we already have duplicates, we expect two duplicates pairs, therefor four datasets
        assert len(duplicates) == 4
        # We expect the third duplicate to be the ignored one
        assert duplicates[2].status == 'IGNORE'

    @staticmethod
    def test_generate_duplicates_no_match(
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        duplicates = matching_service.generate_duplicates(
            existing_matches=[],
            match_radius=1000,
        )
        # If we have a too small radius, we expect no results
        assert len(duplicates) == 0

    @staticmethod
    def test_generate_duplicates_limit_sources(
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        duplicates = matching_service.generate_duplicates(existing_matches=[], match_radius=25000, source_ids=[1])
        # As we just output duplicates where each site is at another source. and we have two selected sources, we
        # expect one duplicates pair, because the other one is between source 2 and 3.
        assert len(duplicates) == 2

    @staticmethod
    def test_apply_duplicates_new(
        db: SQLAlchemy,
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        matching_service.apply_duplicates([[1, 4]], [[4, 1]])
        parking_sites = db.session.query(ParkingSite).all()

        assert len(parking_sites) == 6
        for parking_site in parking_sites:
            if parking_site.id == 4:
                assert parking_site.duplicate_of_parking_site_id == 1
            else:
                assert parking_site.duplicate_of_parking_site_id is None

    @staticmethod
    def test_apply_duplicates_overwrite(
        db: SQLAlchemy,
        multi_source_parking_site_test_data: None,
        matching_service: MatchingService,
    ) -> None:
        parking_site_4 = db.session.get(ParkingSite, 4)
        parking_site_4.duplicate_of_parking_site_id = 1
        matching_service.apply_duplicates([[1, 4], [4, 1]], [])

        parking_sites = db.session.query(ParkingSite).all()

        assert len(parking_sites) == 6
        for parking_site in parking_sites:
            assert parking_site.duplicate_of_parking_site_id is None
