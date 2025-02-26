"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Optional, Union

from requests import request
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

from webapp.common.config import ConfigHelper
from webapp.common.json import DefaultJSONEncoder
from webapp.common.logging import log
from webapp.common.logging.models import LogMessageType

logger = logging.getLogger(__name__)


class RemoteServerType(Enum):
    pass


@dataclass
class RemoteServer:
    url: str
    user: str
    password: str
    cert: Optional[str] = None


class RemoteException(Exception):
    http_status: Optional[int] = None
    data: Optional[dict] = None

    def __init__(self, http_status: Optional[int] = None, data: Optional[dict] = None):
        self.http_status = http_status
        self.data = data


class RemoteHelper:
    config_helper: ConfigHelper

    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    def request(
        self,
        method: str,
        remote_server_type: RemoteServerType,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        binary: bool = False,
        ignore_404: bool = False,
    ) -> Union[dict, list, bytes, None]:
        remote_server = self.config_helper.get('REMOTE_SERVERS')[remote_server_type]
        url = '%s%s' % (remote_server.url, path)
        json_data = json.dumps(data, cls=DefaultJSONEncoder) if data else None
        try:
            response = request(
                method=method,
                params=params,
                url=url,
                auth=(remote_server.user, remote_server.password),
                data=json_data,
                headers={'content-type': 'application/json'},
                verify=remote_server.cert,
                timeout=300,
            )

            log_fragments = [f'{method.upper()} {response.url}: HTTP {response.status_code}']
            if data:
                log_fragments.append(f'>> {data}')
            if response.text and response.text.strip():
                log_fragments.append(f'<< {response.text.strip()}')
            log(
                logger,
                logging.INFO,
                LogMessageType.REQUEST_OUT,
                '\n'.join(log_fragments),
            )

            try:
                if response.status_code == 404 and ignore_404:
                    return response.json()
                if response.status_code not in [200, 201, 202, 204, 404]:
                    raise RemoteException(
                        http_status=response.status_code,
                        data=response.json(),
                    )
                if binary:
                    return response.content
                if response.status_code == 204:
                    return {}
                return response.json()
            except JSONDecodeError as e:
                if ignore_404 and response.status_code == 404:
                    return None
                raise RemoteException(http_status=response.status_code) from e
        except (ConnectionError, NewConnectionError) as e:
            raise RemoteException from e

    def get(self, **kwargs):
        return self.request(method='get', **kwargs)

    def post(self, **kwargs):
        return self.request(method='post', **kwargs)

    def put(self, **kwargs):
        return self.request(method='put', **kwargs)

    def patch(self, **kwargs):
        return self.request(method='patch', **kwargs)

    def delete(self, **kwargs):
        return self.request(method='delete', **kwargs)
