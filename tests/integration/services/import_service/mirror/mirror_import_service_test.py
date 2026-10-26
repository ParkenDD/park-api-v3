"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

import pytest
from requests import HTTPError

from webapp.common.flask_app import App
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.dependencies import dependencies
from webapp.models import ParkingSite, ParkingSpot, Source
from webapp.models.source import SourceStatus
from webapp.services.import_service.generic import GenericImportService
from webapp.services.import_service.mirror import MirrorPullConverter

MIRROR_BASE_URL = 'https://upstream.park-api.example/park-api'

UPSTREAM_SOURCES = {
    'items': [
        {
            'uid': 'other_source',
            'name': 'Other Source',
            'static_status': 'ACTIVE',
            'realtime_status': 'DISABLED',
            'id': 1,
        },
        {
            'uid': 'mirror_source',
            'name': 'Mirror Source',
            'public_url': 'https://mirror-source.example',
            'attribution_license': '',
            'static_status': 'ACTIVE',
            'realtime_status': 'ACTIVE',
            'id': 2,
        },
    ],
    'total_count': 2,
}


def get_upstream_parking_site(counter: int, **kwargs) -> dict[str, Any]:
    return {
        'source_id': 2,
        'original_uid': f'parking-site-{counter}',
        'name': f'Parking Site {counter}',
        'type': 'CAR_PARK',
        'purpose': 'CAR',
        'has_realtime_data': True,
        'static_data_updated_at': '2026-10-25T10:00:00Z',
        'realtime_data_updated_at': '2026-10-25T10:05:00Z',
        'realtime_opening_status': 'OPEN',
        'lat': 49.5,
        'lon': 9.3,
        'official_region_code': '082250014014',
        'capacity': 60,
        'realtime_free_capacity': 30,
        'id': 100 + counter,
        'created_at': '2024-06-05T09:47:46Z',
        'modified_at': '2026-10-25T10:05:00Z',
        **kwargs,
    }


UPSTREAM_PARKING_SPOT = {
    'source_id': 2,
    'original_uid': 'parking-spot-1',
    'parking_site_id': 101,
    'type': 'ON_STREET',
    'purpose': 'CAR',
    'has_realtime_data': True,
    'static_data_updated_at': '2026-10-25T10:00:00Z',
    'realtime_data_updated_at': '2026-10-25T10:05:00Z',
    'realtime_status': 'TAKEN',
    'lat': 49.5,
    'lon': 9.3,
    'id': 200,
    'created_at': '2024-06-05T09:47:46Z',
    'modified_at': '2026-10-25T10:05:00Z',
    'restrictions': [{'type': 'DISABLED'}],
}


class FakeResponse:
    def __init__(self, data: dict | None, status_code: int = 200):
        self.data = data
        self.status_code = status_code

    def json(self) -> dict:
        return self.data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(f'{self.status_code} error')


class FakeUpstream:
    """
    Simulates the public v3 API of an upstream ParkAPI instance with a page size of one item, so that pagination is
    always used.
    """

    def __init__(self, sources: dict, parking_sites: list[dict], parking_spots: list[dict]):
        self.sources = sources
        self.items_by_endpoint = {'parking-sites': parking_sites, 'parking-spots': parking_spots}
        self.requested_params_by_endpoint: dict[str, list[dict]] = {'parking-sites': [], 'parking-spots': []}

    def get(self, url: str, params: dict | None = None, **kwargs) -> FakeResponse:
        path = url.removeprefix(f'{MIRROR_BASE_URL}/api/public/v3/')
        if path == 'sources':
            return FakeResponse(self.sources)

        if path not in self.items_by_endpoint:
            return FakeResponse(None, status_code=404)

        assert params['source_uid'] == 'mirror_source'
        assert params['calculate_has_realtime_data'] == 'false'
        self.requested_params_by_endpoint[path].append(dict(params))

        items = self.items_by_endpoint[path]
        if 'modified_since' in params:
            modified_since = datetime.fromisoformat(params['modified_since'])
            items = [item for item in items if datetime.fromisoformat(item['modified_at']) >= modified_since]
        total_count = len(items)
        items = [item for item in items if item['id'] >= params.get('start', 0)][:1]
        response_data = {'items': items, 'total_count': total_count}
        if items:
            response_data['next_id'] = items[-1]['id'] + 1
        return FakeResponse(response_data)


@pytest.fixture
def fake_upstream(monkeypatch: pytest.MonkeyPatch) -> FakeUpstream:
    fake_upstream = FakeUpstream(
        sources=UPSTREAM_SOURCES,
        parking_sites=[
            get_upstream_parking_site(1, group={'original_uid': 'group-1', 'id': 1}),
            get_upstream_parking_site(2, has_realtime_data=False, realtime_data_updated_at=None),
        ],
        parking_spots=[UPSTREAM_PARKING_SPOT],
    )
    monkeypatch.setattr(
        MirrorPullConverter,
        'request_get',
        lambda self, **kwargs: fake_upstream.get(**kwargs),
    )
    return fake_upstream


@pytest.fixture
def generic_import_service(flask_app: App, fake_upstream: FakeUpstream) -> GenericImportService:
    # Trailing slash is optional at mirror_base_url
    flask_app.config['PARK_API_CONVERTER'] = [{'uid': 'mirror_source', 'mirror_base_url': f'{MIRROR_BASE_URL}/'}]
    service = GenericImportService(
        source_repository=dependencies.get_source_repository(),
        generic_parking_site_import_service=dependencies.get_generic_parking_site_import_service(),
        generic_parking_spot_import_service=dependencies.get_generic_parking_spot_import_service(),
        **dependencies.get_base_service_dependencies(),
    )
    service.init_app(flask_app)
    return service


class MirrorImportServiceTest:
    @staticmethod
    def test_mirror_source_is_pull_source(generic_import_service: GenericImportService) -> None:
        converter = generic_import_service.park_api_sources.converter_by_uid['mirror_source']
        assert isinstance(converter, MirrorPullConverter)
        assert generic_import_service.is_pull_source('mirror_source')

    @staticmethod
    def test_update_source_static_and_realtime(db: SQLAlchemy, generic_import_service: GenericImportService) -> None:
        generic_import_service.update_source_static('mirror_source')
        generic_import_service.update_source_realtime('mirror_source')

        source = db.session.query(Source).one()
        assert source.uid == 'mirror_source'
        assert source.name == 'Mirror Source'
        assert source.public_url == 'https://mirror-source.example'
        assert source.attribution_license is None
        assert source.static_status == SourceStatus.ACTIVE
        assert source.realtime_status == SourceStatus.ACTIVE

        parking_sites = db.session.query(ParkingSite).order_by(ParkingSite.original_uid).all()
        assert [parking_site.original_uid for parking_site in parking_sites] == ['parking-site-1', 'parking-site-2']
        assert parking_sites[0].parking_site_group.original_uid == 'group-1'
        assert parking_sites[0].has_realtime_data is True
        assert parking_sites[0].realtime_free_capacity == 30
        assert parking_sites[1].parking_site_group_id is None
        assert parking_sites[1].has_realtime_data is False
        assert parking_sites[1].realtime_free_capacity is None

        parking_spot = db.session.query(ParkingSpot).one()
        assert parking_spot.original_uid == 'parking-spot-1'
        assert parking_spot.parking_site_id == parking_sites[0].id
        assert parking_spot.realtime_status.value == 'TAKEN'

    @staticmethod
    def test_update_source_static_deletes_removed_parking_sites(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        fake_upstream: FakeUpstream,
    ) -> None:
        generic_import_service.update_source_static('mirror_source')
        fake_upstream.items_by_endpoint['parking-sites'] = fake_upstream.items_by_endpoint['parking-sites'][:1]
        generic_import_service.update_source_static('mirror_source')

        parking_sites = db.session.query(ParkingSite).all()
        assert [parking_site.original_uid for parking_site in parking_sites] == ['parking-site-1']

    @staticmethod
    def test_update_source_static_unknown_upstream_source(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        fake_upstream: FakeUpstream,
    ) -> None:
        fake_upstream.sources = {'items': UPSTREAM_SOURCES['items'][:1], 'total_count': 1}

        generic_import_service.update_source_static('mirror_source')

        source = db.session.query(Source).one()
        assert source.static_status == SourceStatus.FAILED
        assert db.session.query(ParkingSite).count() == 0

    @staticmethod
    def test_update_source_realtime_is_incremental(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        fake_upstream: FakeUpstream,
    ) -> None:
        fake_upstream.items_by_endpoint['parking-sites'].append(
            get_upstream_parking_site(3, modified_at='2026-10-25T10:01:00Z'),
        )
        generic_import_service.update_source_static('mirror_source')

        # The first realtime pull is a full pull
        generic_import_service.update_source_realtime('mirror_source')

        source = db.session.query(Source).one()
        assert source.mirror_parking_site_cursor == datetime(2026, 10, 25, 10, 5, tzinfo=timezone.utc)
        assert source.mirror_parking_spot_cursor == datetime(2026, 10, 25, 10, 5, tzinfo=timezone.utc)
        assert 'mirror_parking_site_cursor' not in source.to_dict()
        assert 'modified_since' not in fake_upstream.requested_params_by_endpoint['parking-sites'][-1]

        # parking-site-1 changes upstream, parking-site-3 is too old to be part of the incremental pull
        fake_upstream.items_by_endpoint['parking-sites'][0].update(
            realtime_free_capacity=10,
            realtime_data_updated_at='2026-10-25T10:10:00Z',
            modified_at='2026-10-25T10:10:00Z',
        )
        fake_upstream.items_by_endpoint['parking-sites'][2]['realtime_free_capacity'] = 20

        generic_import_service.update_source_realtime('mirror_source')

        # The cursor minus one minute overlap is used
        params = fake_upstream.requested_params_by_endpoint['parking-sites'][-1]
        assert datetime.fromisoformat(params['modified_since']) == datetime(2026, 10, 25, 10, 4, tzinfo=timezone.utc)
        params = fake_upstream.requested_params_by_endpoint['parking-spots'][-1]
        assert datetime.fromisoformat(params['modified_since']) == datetime(2026, 10, 25, 10, 4, tzinfo=timezone.utc)

        source = db.session.query(Source).one()
        assert source.realtime_status == SourceStatus.ACTIVE
        assert source.mirror_parking_site_cursor == datetime(2026, 10, 25, 10, 10, tzinfo=timezone.utc)
        assert source.mirror_parking_spot_cursor == datetime(2026, 10, 25, 10, 5, tzinfo=timezone.utc)

        parking_sites = db.session.query(ParkingSite).order_by(ParkingSite.original_uid).all()
        assert parking_sites[0].realtime_free_capacity == 10
        assert parking_sites[2].realtime_free_capacity == 30

    @staticmethod
    def test_update_source_static_resets_cursors(
        db: SQLAlchemy,
        generic_import_service: GenericImportService,
        fake_upstream: FakeUpstream,
    ) -> None:
        generic_import_service.update_source_static('mirror_source')
        generic_import_service.update_source_realtime('mirror_source')
        generic_import_service.update_source_static('mirror_source')

        source = db.session.query(Source).one()
        assert source.mirror_parking_site_cursor is None
        assert source.mirror_parking_spot_cursor is None

        generic_import_service.update_source_realtime('mirror_source')

        assert 'modified_since' not in fake_upstream.requested_params_by_endpoint['parking-sites'][-1]
        assert 'modified_since' not in fake_upstream.requested_params_by_endpoint['parking-spots'][-1]
