"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from celery.schedules import crontab
from parkapi_sources.converters.base_converter.pull import PullConverter

from webapp.common.celery import CeleryHelper
from webapp.common.config import ConfigHelper
from webapp.common.logging import Logger
from webapp.extensions import celery

from .generic_import_heartbeat_tasks import realtime_import_task, static_import_task
from .generic_import_service import ParkingSiteGenericImportService


class GenericImportRunner:
    celery_helper: CeleryHelper
    logger: Logger
    config_helper: ConfigHelper
    parking_site_generic_import_service: ParkingSiteGenericImportService

    def __init__(
        self,
        celery_helper: CeleryHelper,
        logger: Logger,
        config_helper: ConfigHelper,
        parking_site_generic_import_service: ParkingSiteGenericImportService,
    ):
        self.celery_helper = celery_helper
        self.logger = logger
        self.config_helper = config_helper
        self.parking_site_generic_import_service = parking_site_generic_import_service

    def start(self):
        for source_uid in self.parking_site_generic_import_service.park_api_sources.converter_by_uid.keys():
            # Don't try to pull push-endpoints
            if not isinstance(
                self.parking_site_generic_import_service.park_api_sources.converter_by_uid[source_uid],
                PullConverter,
            ):
                continue

            celery.add_periodic_task(
                crontab(
                    minute=str(self.config_helper.get('PARKING_SITE_STATIC_PULL_MINUTE', 0)),
                    hour=str(self.config_helper.get('PARKING_SITE_STATIC_PULL_HOUR', 1)),
                ),
                static_import_task,
                kwargs={'source': source_uid},
            )

            celery.add_periodic_task(
                self.config_helper.get('PARKING_SITE_REALTIME_PULL_FREQUENCY', 5 * 60),
                realtime_import_task,
                kwargs={'source': source_uid},
            )