"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import MagicMock

import pytest
from parkapi_sources.util import RequestHelper
from requests import Session

from webapp.common.flask_app import App
from webapp.common.remote_helper import RemoteHelper, RemoteServer, RemoteServerType
from webapp.dependencies import dependencies
from webapp.services.import_service.generic import GenericImportService

MIRROR_BASE_URL = 'https://upstream.park-api.example/park-api'


class TestRemoteServerType(RemoteServerType):
    TEST = 'TEST'


@pytest.fixture
def session_request_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    session_request_mock = MagicMock()

    def session_request(self: Session, **kwargs):
        session_request_mock(headers=dict(self.headers), **kwargs)
        response = MagicMock()
        response.json.return_value = {'items': [{'uid': 'mirror_source', 'name': 'Mirror Source'}]}
        return response

    monkeypatch.setattr(Session, 'request', session_request)
    return session_request_mock


def get_mirror_request_user_agent(flask_app: App, session_request_mock: MagicMock) -> str:
    flask_app.config['PARK_API_CONVERTER'] = [{'uid': 'mirror_source', 'mirror_base_url': MIRROR_BASE_URL}]
    service = GenericImportService(
        source_repository=dependencies.get_source_repository(),
        generic_parking_site_import_service=dependencies.get_generic_parking_site_import_service(),
        generic_parking_spot_import_service=dependencies.get_generic_parking_spot_import_service(),
        **dependencies.get_base_service_dependencies(),
    )
    service.init_app(flask_app)
    service.park_api_sources.converter_by_uid['mirror_source'].update_source_info()

    return session_request_mock.call_args.kwargs['headers']['User-Agent']


def get_remote_request_user_agent(flask_app: App, monkeypatch: pytest.MonkeyPatch) -> str:
    flask_app.config['REMOTE_SERVERS'] = {
        TestRemoteServerType.TEST: RemoteServer(url='https://remote.example', user='user', password='password'),
    }
    request_mock = MagicMock()
    request_mock.return_value.status_code = 204
    monkeypatch.setattr('webapp.common.remote_helper.request', request_mock)

    RemoteHelper(config_helper=dependencies.get_config_helper()).get(
        remote_server_type=TestRemoteServerType.TEST,
        path='/test',
    )

    return request_mock.call_args.kwargs['headers']['User-Agent']


class UserAgentTest:
    @staticmethod
    def test_default_user_agent(
        flask_app: App,
        session_request_mock: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        flask_app.config['USER_AGENT'] = None

        assert get_mirror_request_user_agent(flask_app, session_request_mock) == RequestHelper.DEFAULT_USER_AGENT
        assert get_remote_request_user_agent(flask_app, monkeypatch) == RequestHelper.DEFAULT_USER_AGENT

    @staticmethod
    def test_configured_user_agent(
        flask_app: App,
        session_request_mock: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        flask_app.config['USER_AGENT'] = 'CustomParkAPI/1.0'

        assert get_mirror_request_user_agent(flask_app, session_request_mock) == 'CustomParkAPI/1.0'
        assert get_remote_request_user_agent(flask_app, monkeypatch) == 'CustomParkAPI/1.0'
