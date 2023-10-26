"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask.cli import AppGroup

from webapp.dependencies import dependencies
from webapp.services.import_service import ParkingSiteGenericImportService

source_cli = AppGroup('source', help='Source related commands')


@source_cli.command('init-converters', help='init converters')
def cli_source_init_converters():
    parking_site_import_generic_service = ParkingSiteGenericImportService(
        parking_site_repository=dependencies.get_parking_site_repository(),
        source_repository=dependencies.get_source_repository(),
        **dependencies.get_base_service_dependencies(),
    )
    parking_site_import_generic_service.update_sources_static()
    parking_site_import_generic_service.update_source_realtime()
