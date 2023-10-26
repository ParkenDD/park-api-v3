"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.dependencies import dependencies
from webapp.extensions import celery
from webapp.services.import_service import ParkingSiteGenericImportService
from .base_task import BaseTask


class RunGenericRealtimeImportTask(BaseTask):
    run_interval = 5

    @staticmethod
    @celery.task()
    def task(source: str):
        parking_site_import_generic_service = ParkingSiteGenericImportService(
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
            **dependencies.get_base_service_dependencies(),
        )
        parking_site_import_generic_service.update_source_realtime(source)
