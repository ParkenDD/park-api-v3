"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from webapp.dependencies import dependencies
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
