"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging

from flask import Response, request

from webapp.common.blueprint import Blueprint
from webapp.common.contexts import TelemetryContext
from webapp.common.logging import log
from webapp.common.logging.models import LogMessageType
from webapp.dependencies import dependencies

from .base_blueprint import AdminApiBaseBlueprint
from .generic import GenericBlueprint
from .parking_sites import ParkingSitesBlueprint
from .parking_spots import ParkingSpotBlueprint
from .sources import SourceBlueprint

logger = logging.getLogger(__name__)


class AdminRestApi(Blueprint):
    documentation_base = True
    documentation_auth = 'basic'

    blueprints_classes: list[type[AdminApiBaseBlueprint]] = [
        GenericBlueprint,
        ParkingSitesBlueprint,
        ParkingSpotBlueprint,
        SourceBlueprint,
    ]

    def __init__(self):
        super().__init__('admin', __name__, url_prefix='/api/admin/v1')

        for blueprint_class in self.blueprints_classes:
            self.register_blueprint(blueprint_class())

        @self.before_request
        def before_request(*args, **kwargs):
            context_helper = dependencies.get_context_helper()
            context_helper.set_telemetry_context(TelemetryContext.INITIATOR, 'admin-api')

        @self.after_request
        def after_request(response: Response):
            if not request.path.startswith('/api/admin/v1'):
                return response

            log_fragments = [f'{request.method.upper()} {request.full_path}: HTTP {response.status}']
            if request.data:
                if request.mimetype == 'application/json':
                    log_fragments.append(f'>> {request.data.decode()}')
                else:
                    log_fragments.append(f'>> binary data with {len(request.data)} byte')
            if response.data and response.data.decode().strip():
                log_fragments.append(f'<< {response.data.decode().strip()}')

            log(logger, logging.INFO, LogMessageType.REQUEST_IN, '\n'.join(log_fragments))

            return response
