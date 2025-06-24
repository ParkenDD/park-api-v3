"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from celery.schedules import crontab
from parkapi_sources.converters.base_converter.pull import PullConverter

from webapp.common.celery import CeleryHelper
from webapp.common.config import ConfigHelper
from webapp.extensions import celery

from .generic_import_heartbeat_tasks import realtime_import_task, static_import_task
from .generic_import_service import GenericImportService


class GenericImportRunner:
    celery_helper: CeleryHelper
    config_helper: ConfigHelper
    generic_import_service: GenericImportService

    def __init__(
        self,
        celery_helper: CeleryHelper,
        config_helper: ConfigHelper,
        generic_import_service: GenericImportService,
    ):
        self.celery_helper = celery_helper
        self.config_helper = config_helper
        self.generic_import_service = generic_import_service

    def start(self):
        for source_uid in self.generic_import_service.park_api_sources.converter_by_uid.keys():
            # Don't try to pull push-endpoints
            if not isinstance(
                self.generic_import_service.park_api_sources.converter_by_uid[source_uid],
                PullConverter,
            ):
                continue

            celery.add_periodic_task(
                crontab(
                    minute=str(self.config_helper.get('STATIC_IMPORT_PULL_MINUTE')),
                    hour=str(self.config_helper.get('STATIC_IMPORT_PULL_HOUR')),
                ),
                static_import_task,
                kwargs={'source': source_uid},
            )

            celery.add_periodic_task(
                self.config_helper.get('REALTIME_IMPORT_PULL_FREQUENCY'),
                realtime_import_task,
                kwargs={'source': source_uid},
            )
