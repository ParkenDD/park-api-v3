"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.dependencies import dependencies
from webapp.extensions import celery


@celery.task()
def static_import_task(source: str):
    generic_import_generic_service = dependencies.get_generic_import_service()
    generic_import_generic_service.update_source_static(source)


@celery.task()
def realtime_import_task(source: str):
    generic_import_generic_service = dependencies.get_generic_import_service()
    generic_import_generic_service.update_source_realtime(source)
