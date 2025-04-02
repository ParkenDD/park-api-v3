"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from unittest.mock import ANY

import pytest
from parkapi_sources.converters.base_converter import ParkingSpotBaseConverter
from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import RealtimeParkingSpotInput, SourceInfo, StaticParkingSpotInput
from parkapi_sources.models.enums import ParkingSpotStatus
from parkapi_sources.util import ConfigHelper, RequestHelper

from tests.integration.services.import_service.generic.parking_spot_response_data import (
    CREATE_PARKING_SPOT_REALTIME_DATA,
    CREATE_PARKING_SPOT_STATIC_DATA,
    CREATE_PARKING_SPOT_WITH_PARKING_RESTRICTIONS_DATA,
)
from tests.model_generator.parking_restriction import get_parking_restriction_input
from tests.model_generator.parking_spot import get_realtime_parking_spot_input, get_static_parking_spot_input
from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.dependencies import dependencies
from webapp.models import ParkingSpot
from webapp.services.import_service.generic import GenericImportService


class ParkingSpotTestPullConverter(PullConverter, ParkingSpotBaseConverter):
    source_info = SourceInfo(
        uid='source',
        name='Test',
        has_realtime_data=True,
    )

    get_static_parking_spots_return_value: tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]
    get_realtime_parking_spots_return_value: tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        return self.get_static_parking_spots_return_value

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        return self.get_realtime_parking_spots_return_value


@pytest.fixture
def park_api_sources_config_helper() -> ConfigHelper:
    return ConfigHelper({})


@pytest.fixture
def park_api_sources_request_helper(park_api_sources_config_helper: ConfigHelper) -> RequestHelper:
    return RequestHelper(config_helper=park_api_sources_config_helper)


@pytest.fixture
def parking_spot_test_pull_converter(
    park_api_sources_config_helper: ConfigHelper,
    park_api_sources_request_helper: RequestHelper,
) -> ParkingSpotTestPullConverter:
    return ParkingSpotTestPullConverter(
        config_helper=park_api_sources_config_helper,
        request_helper=park_api_sources_request_helper,
    )


@pytest.fixture
def flask_app_with_test_sources(flask_app: App, parking_spot_test_pull_converter: ParkingSpotTestPullConverter) -> App:
    flask_app.config['PARK_API_SOURCES_CUSTOM_CONVERTERS'] = [parking_spot_test_pull_converter]
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
    def test_update_sources_create_parking_spot_static(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_spot_test_pull_converter: ParkingSpotTestPullConverter,
    ) -> None:
        parking_spot_test_pull_converter.get_static_parking_spots_return_value = (
            [get_static_parking_spot_input()],
            [],
        )
        generic_import_service.update_sources_static()

        parking_spots = db.session.query(ParkingSpot).all()

        assert len(parking_spots) == 1
        assert parking_spots[0].to_dict() == CREATE_PARKING_SPOT_STATIC_DATA

    @staticmethod
    def test_update_sources_create_parking_spot_realtime(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_spot_test_pull_converter: ParkingSpotTestPullConverter,
    ) -> None:
        parking_spot_test_pull_converter.get_static_parking_spots_return_value = (
            [get_static_parking_spot_input()],
            [],
        )
        parking_spot_test_pull_converter.get_realtime_parking_spots_return_value = (
            [get_realtime_parking_spot_input()],
            [],
        )
        generic_import_service.update_sources_static()
        generic_import_service.update_sources_realtime()

        parking_spots = db.session.query(ParkingSpot).all()

        assert len(parking_spots) == 1
        assert parking_spots[0].to_dict() == CREATE_PARKING_SPOT_REALTIME_DATA

    @staticmethod
    def test_update_sources_create_parking_spot_with_restricted_to(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        parking_spot_test_pull_converter: ParkingSpotTestPullConverter,
    ) -> None:
        parking_spot_test_pull_converter.get_static_parking_spots_return_value = (
            [get_static_parking_spot_input(restricted_to=[get_parking_restriction_input()])],
            [],
        )
        generic_import_service.update_sources_static()

        parking_spots = db.session.query(ParkingSpot).all()

        assert len(parking_spots) == 1
        parking_spot_dict = parking_spots[0].to_dict(include_parking_restrictions=True)
        assert parking_spot_dict == CREATE_PARKING_SPOT_WITH_PARKING_RESTRICTIONS_DATA

    @staticmethod
    def test_update_sources_update_parking_spot_static(
        db: SQLAlchemy,
        inserted_parking_spot: ParkingSpot,
        generic_import_service: GenericImportService,
        parking_spot_test_pull_converter: ParkingSpotTestPullConverter,
    ) -> None:
        parking_spot_input = get_static_parking_spot_input(name='Updated Name')
        parking_spot_test_pull_converter.get_static_parking_spots_return_value = (
            [parking_spot_input],
            [],
        )
        generic_import_service.update_sources_static()

        parking_spots = db.session.query(ParkingSpot).all()

        assert len(parking_spots) == 1
        expected_response = deepcopy(CREATE_PARKING_SPOT_STATIC_DATA)
        expected_response['name'] = 'Updated Name'
        expected_response['static_data_updated_at'] = parking_spot_input.static_data_updated_at
        expected_response['realtime_data_updated_at'] = ANY
        expected_response['realtime_status'] = ParkingSpotStatus.AVAILABLE
        assert parking_spots[0].to_dict() == expected_response

    @staticmethod
    def test_update_sources_update_parking_spot_realtime(
        db: SQLAlchemy,
        inserted_parking_spot: ParkingSpot,
        generic_import_service: GenericImportService,
        parking_spot_test_pull_converter: ParkingSpotTestPullConverter,
    ) -> None:
        parking_spot_input = get_realtime_parking_spot_input(realtime_status=ParkingSpotStatus.TAKEN)
        parking_spot_test_pull_converter.get_realtime_parking_spots_return_value = (
            [parking_spot_input],
            [],
        )
        generic_import_service.update_sources_realtime()

        parking_spots = db.session.query(ParkingSpot).all()

        assert len(parking_spots) == 1
        expected_response = deepcopy(CREATE_PARKING_SPOT_REALTIME_DATA)
        expected_response['static_data_updated_at'] = ANY
        expected_response['realtime_data_updated_at'] = parking_spot_input.realtime_data_updated_at
        expected_response['realtime_status'] = ParkingSpotStatus.TAKEN
        assert parking_spots[0].to_dict() == expected_response
