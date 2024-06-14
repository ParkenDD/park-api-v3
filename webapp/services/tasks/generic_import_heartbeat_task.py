"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.dependencies import dependencies
from webapp.extensions import celery

from .base_task import BaseTask


class RunGenericRealtimeImportTask(BaseTask):
    run_interval = 5 * 60  # 5 minutes

    @staticmethod
    @celery.task()
    def task(source: str):
        parking_site_import_generic_service = dependencies.get_parking_site_generic_import_service()
        parking_site_import_generic_service.update_source_realtime(source)


class RunGenericStaticImportTask(BaseTask):
    run_interval = 60 * 60 * 24  # 24 hours

    @staticmethod
    @celery.task()
    def task(source: str):
        parking_site_import_generic_service = dependencies.get_parking_site_generic_import_service()
        parking_site_import_generic_service.update_source_static(source)
