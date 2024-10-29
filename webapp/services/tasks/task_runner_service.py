"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter.pull import PullConverter

from webapp.common.celery import CeleryHelper
from webapp.common.config import ConfigHelper
from webapp.common.logging import Logger
from webapp.extensions import celery
from webapp.services.import_service import ParkingSiteGenericImportService

from .base_task import BaseTask
from .generic_import_heartbeat_task import RunGenericRealtimeImportTask, RunGenericStaticImportTask


class TaskRunner:
    tasks: list[type[BaseTask]] = []
    generic_static_import_task: RunGenericStaticImportTask
    generic_realtime_import_task: RunGenericRealtimeImportTask
    task_instances: list[BaseTask]

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
        self.task_instances = []
        self.logger = logger
        self.config_helper = config_helper
        self.parking_site_generic_import_service = parking_site_generic_import_service

        for task in self.tasks:
            self.task_instances.append(task())
        self.generic_static_import_task = RunGenericStaticImportTask()
        self.generic_realtime_import_task = RunGenericRealtimeImportTask()

    def start(self):
        for task in self.task_instances:
            celery.add_periodic_task(task.run_interval, task.task)

        # Add parameterized tasks
        for source_uid in self.parking_site_generic_import_service.park_api_sources.converter_by_uid.keys():
            # Don't try to pull push-endpoints
            if not isinstance(
                self.parking_site_generic_import_service.park_api_sources.converter_by_uid[source_uid],
                PullConverter,
            ):
                continue

            celery.add_periodic_task(
                self.generic_static_import_task.run_interval,
                self.generic_static_import_task.task,
                kwargs={'source': source_uid},
            )
            celery.add_periodic_task(
                self.generic_realtime_import_task.run_interval,
                self.generic_realtime_import_task.task,
                kwargs={'source': source_uid},
            )
