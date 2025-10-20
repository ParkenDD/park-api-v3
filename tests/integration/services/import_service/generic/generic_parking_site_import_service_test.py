"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy

import pytest
from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import ConfigHelper, RequestHelper

from tests.integration.services.import_service.generic.parking_site_response_data import (
    CREATE_PARKING_SITE_REALTIME_DATA,
    CREATE_PARKING_SITE_STATIC_DATA,
)
from tests.model_generator.parking_site import get_realtime_parking_site_input, get_static_parking_site_input
from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.dependencies import dependencies
from webapp.models import ParkingSite
from webapp.services.import_service.generic import GenericImportService


class ParkingSiteTestPullConverter(ParkingSitePullConverter):
    source_info = SourceInfo(
        uid='source',
        name='Test',
        has_realtime_data=True,
    )

    get_static_parking_sites_return_value: tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]
    get_realtime_parking_sites_return_value: tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self.get_static_parking_sites_return_value

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self.get_realtime_parking_sites_return_value


@pytest.fixture
def park_api_sources_config_helper() -> ConfigHelper:
    return ConfigHelper({})


@pytest.fixture
def park_api_sources_request_helper(park_api_sources_config_helper: ConfigHelper) -> RequestHelper:
    return RequestHelper(config_helper=park_api_sources_config_helper)


@pytest.fixture
def parking_site_test_pull_converter(
    park_api_sources_config_helper: ConfigHelper,
    park_api_sources_request_helper: RequestHelper,
) -> ParkingSiteTestPullConverter:
    return ParkingSiteTestPullConverter(
        config_helper=park_api_sources_config_helper,
        request_helper=park_api_sources_request_helper,
    )


@pytest.fixture
def flask_app_with_test_sources(
    flask_app: App,
    parking_site_test_pull_converter: ParkingSiteTestPullConverter,
) -> App:
    flask_app.config['PARK_API_SOURCES_CUSTOM_CONVERTERS'] = [parking_site_test_pull_converter]
    return flask_app


@pytest.fixture
def generic_import_service(flask_app_with_test_sources: App) -> GenericImportService:
    service = GenericImportService(
        source_repository=dependencies.get_source_repository(),
        generic_parking_site_import_service=dependencies.get_generic_parking_site_import_service(),
        generic_parking_spot_import_service=dependencies.get_generic_parking_spot_import_service(),
        **dependencies.get_base_service_dependencies(),
    )
    service.init_app(flask_app_with_test_sources)
    return service


class GenericImportServiceTest:
    @staticmethod
    def test_update_sources_create_parking_site_static(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_site_test_pull_converter: ParkingSiteTestPullConverter,
    ) -> None:
        parking_site_test_pull_converter.get_static_parking_sites_return_value = (
            [get_static_parking_site_input()],
            [],
        )
        generic_import_service.update_sources_static()

        parking_sites = db.session.query(ParkingSite).all()

        assert len(parking_sites) == 1
        assert parking_sites[0].to_dict() == CREATE_PARKING_SITE_STATIC_DATA

    @staticmethod
    def test_update_sources_create_parking_site_realtime(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_site_test_pull_converter: ParkingSiteTestPullConverter,
    ) -> None:
        parking_site_test_pull_converter.get_static_parking_sites_return_value = (
            [get_static_parking_site_input()],
            [],
        )
        parking_site_test_pull_converter.get_realtime_parking_sites_return_value = (
            [get_realtime_parking_site_input()],
            [],
        )
        generic_import_service.update_sources_static()
        generic_import_service.update_sources_realtime()

        parking_sites = db.session.query(ParkingSite).all()

        assert len(parking_sites) == 1
        assert parking_sites[0].to_dict() == CREATE_PARKING_SITE_REALTIME_DATA

    @staticmethod
    def test_update_sources_create_parking_site_realtime_too_many_realtime(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_site_test_pull_converter: ParkingSiteTestPullConverter,
    ) -> None:
        parking_site_test_pull_converter.get_static_parking_sites_return_value = (
            [get_static_parking_site_input()],
            [],
        )
        parking_site_test_pull_converter.get_realtime_parking_sites_return_value = (
            [get_realtime_parking_site_input(realtime_free_capacity=50)],
            [],
        )
        generic_import_service.update_sources_static()
        generic_import_service.update_sources_realtime()

        parking_sites = db.session.query(ParkingSite).all()

        assert len(parking_sites) == 1
        expected_response = deepcopy(CREATE_PARKING_SITE_REALTIME_DATA)
        # Should be cut to capacity
        expected_response['realtime_free_capacity'] = 10
        assert parking_sites[0].to_dict() == expected_response
