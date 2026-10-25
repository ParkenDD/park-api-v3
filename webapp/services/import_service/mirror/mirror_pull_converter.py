"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Generator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter, ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    SourceInfo,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)
from parkapi_sources.util import ConfigHelper, RequestHelper
from validataclass.exceptions import ValidationError

from webapp.services.import_service.exceptions import MirrorSourceNotFoundException


class MirrorPullConverter(ParkingSitePullConverter, ParkingSpotPullConverter):
    """
    Pulls parking sites and parking spots of a single source from the public v3 API of another ParkAPI instance. The
    source metadata is taken from the upstream instance, too, and gets updated with every static pull.
    """

    mirror_base_url: str
    page_limit: int = 1000

    _source_info: SourceInfo
    # Upstream parking site ids mapped to upstream parking site original uids, used to link parking spots
    _parking_site_uid_by_id: dict[int, str]

    def __init__(
        self,
        *,
        config_helper: ConfigHelper,
        request_helper: RequestHelper,
        source_uid: str,
        mirror_base_url: str,
    ):
        super().__init__(config_helper=config_helper, request_helper=request_helper)
        self.mirror_base_url = mirror_base_url.rstrip('/')
        # Placeholder until the real source info gets fetched from upstream at update_source_info()
        self._source_info = SourceInfo(uid=source_uid, name=source_uid, has_realtime_data=None)
        self._parking_site_uid_by_id = {}

    @property
    def source_info(self) -> SourceInfo:
        return self._source_info

    def update_source_info(self) -> None:
        response = self.request_get(url=f'{self.mirror_base_url}/api/public/v3/sources')
        response.raise_for_status()

        for source_dict in response.json().get('items', []):
            if source_dict.get('uid') != self.source_info.uid:
                continue

            self._source_info = SourceInfo(
                uid=self.source_info.uid,
                name=source_dict['name'],
                has_realtime_data=source_dict.get('realtime_status') != 'DISABLED',
                public_url=source_dict.get('public_url') or None,
                attribution_license=source_dict.get('attribution_license') or None,
                attribution_url=source_dict.get('attribution_url') or None,
                attribution_contributor=source_dict.get('attribution_contributor') or None,
            )
            return

        raise MirrorSourceNotFoundException(
            message=f'Source {self.source_info.uid} not found at {self.mirror_base_url}',
        )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        parking_site_uid_by_id: dict[int, str] = {}
        for parking_site_dict in self._get_items('parking-sites'):
            parking_site_uid_by_id[parking_site_dict['id']] = parking_site_dict['original_uid']
            try:
                static_parking_site_inputs.append(
                    self.static_parking_site_validator.validate(self._map_parking_site_dict(parking_site_dict)),
                )
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('original_uid'),
                        message=f'Invalid data at uid {parking_site_dict.get("original_uid")}: {e.to_dict()}, '
                        f'data: {parking_site_dict}',
                    ),
                )
        self._parking_site_uid_by_id = parking_site_uid_by_id

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        for parking_site_dict in self._get_items('parking-sites'):
            if not parking_site_dict.get('has_realtime_data') or not parking_site_dict.get('realtime_data_updated_at'):
                continue
            try:
                realtime_parking_site_inputs.append(
                    self.realtime_parking_site_validator.validate(
                        {**parking_site_dict, 'uid': parking_site_dict['original_uid']},
                    ),
                )
            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('original_uid'),
                        message=f'Invalid data at uid {parking_site_dict.get("original_uid")}: {e.to_dict()}, '
                        f'data: {parking_site_dict}',
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        static_parking_spot_errors: list[ImportParkingSpotException] = []

        for parking_spot_dict in self._get_items('parking-spots'):
            try:
                static_parking_spot_inputs.append(
                    self.static_parking_spot_validator.validate(self._map_parking_spot_dict(parking_spot_dict)),
                )
            except ValidationError as e:
                static_parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=parking_spot_dict.get('original_uid'),
                        message=f'Invalid data at uid {parking_spot_dict.get("original_uid")}: {e.to_dict()}, '
                        f'data: {parking_spot_dict}',
                    ),
                )

        return static_parking_spot_inputs, static_parking_spot_errors

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []
        realtime_parking_spot_errors: list[ImportParkingSpotException] = []

        for parking_spot_dict in self._get_items('parking-spots'):
            if not parking_spot_dict.get('has_realtime_data') or not parking_spot_dict.get('realtime_data_updated_at'):
                continue
            try:
                realtime_parking_spot_inputs.append(
                    self.realtime_parking_spot_validator.validate(
                        {**parking_spot_dict, 'uid': parking_spot_dict['original_uid']},
                    ),
                )
            except ValidationError as e:
                realtime_parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=parking_spot_dict.get('original_uid'),
                        message=f'Invalid data at uid {parking_spot_dict.get("original_uid")}: {e.to_dict()}, '
                        f'data: {parking_spot_dict}',
                    ),
                )

        return realtime_parking_spot_inputs, realtime_parking_spot_errors

    def _get_items(self, endpoint: str) -> Generator[dict[str, Any], None, None]:
        """
        Iterates over all items of a paginated upstream endpoint. The upstream next_path is not used, because it does
        not contain the path prefix of mirror_base_url.
        """
        params: dict[str, Any] = {
            'source_uid': self.source_info.uid,
            'limit': self.page_limit,
            # We want the raw realtime state of upstream, the outdating calculation is done locally
            'calculate_has_realtime_data': 'false',
        }
        while True:
            response = self.request_get(url=f'{self.mirror_base_url}/api/public/v3/{endpoint}', params=params)
            response.raise_for_status()
            response_data = response.json()

            yield from response_data.get('items', [])

            if not response_data.get('items') or response_data.get('next_id') is None:
                return
            params['start'] = response_data['next_id']

    @staticmethod
    def _map_parking_site_dict(parking_site_dict: dict[str, Any]) -> dict[str, Any]:
        input_dict = {key: value for key, value in parking_site_dict.items() if key not in ['original_uid', 'group']}
        input_dict['uid'] = parking_site_dict['original_uid']
        if parking_site_dict.get('group'):
            input_dict['group_uid'] = parking_site_dict['group']['original_uid']
        return input_dict

    def _map_parking_spot_dict(self, parking_spot_dict: dict[str, Any]) -> dict[str, Any]:
        input_dict = {
            key: value for key, value in parking_spot_dict.items() if key not in ['original_uid', 'parking_site_id']
        }
        input_dict['uid'] = parking_spot_dict['original_uid']
        if parking_spot_dict.get('parking_site_id') is not None:
            input_dict['parking_site_uid'] = self._get_parking_site_uid(parking_spot_dict['parking_site_id'])
        return input_dict

    def _get_parking_site_uid(self, parking_site_id: int) -> str:
        # Parking sites get cached at static parking site pull, which happens right before the static parking spot pull
        if parking_site_id not in self._parking_site_uid_by_id:
            response = self.request_get(url=f'{self.mirror_base_url}/api/public/v3/parking-sites/{parking_site_id}')
            response.raise_for_status()
            self._parking_site_uid_by_id[parking_site_id] = response.json()['original_uid']
        return self._parking_site_uid_by_id[parking_site_id]
