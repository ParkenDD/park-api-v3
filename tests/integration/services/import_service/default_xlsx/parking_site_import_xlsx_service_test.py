"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

import pytest
from openpyxl import Workbook
from parkapi_sources.models.enums import ParkingAudience

from tests.model_generator.parking_restriction import get_parking_restriction
from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp.common.sqlalchemy import SQLAlchemy
from webapp.dependencies import dependencies
from webapp.models import ParkingSite
from webapp.services.import_service import ParkingSiteXlsxImportService

XLSX_HEADER = [
    'ID',
    'Name',
    'Art der Anlage',
    'Längengrad',
    'Breitengrad',
    'Anzahl Stellplätze',
    'Anzahl Carsharing-Parkplätze',
    'Anzahl Ladeplätze',
    'Anzahl Frauenparkplätze',
    'Anzahl Behindertenparkplätze',
]


@pytest.fixture
def parking_site_xlsx_import_service(db: SQLAlchemy) -> ParkingSiteXlsxImportService:
    return ParkingSiteXlsxImportService(
        parking_site_repository=dependencies.get_parking_site_repository(),
        source_repository=dependencies.get_source_repository(),
        **dependencies.get_base_service_dependencies(),
    )


def write_xlsx(path: Path, rows: list[list]) -> Path:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(XLSX_HEADER)
    for row in rows:
        worksheet.append(row)
    workbook.save(path)
    return path


def get_restriction_capacities(parking_site: ParkingSite) -> dict[ParkingAudience, int | None]:
    return {restriction.type: restriction.capacity for restriction in parking_site.restrictions}


def test_xlsx_import_maps_capacities_to_restrictions(
    db: SQLAlchemy,
    parking_site_xlsx_import_service: ParkingSiteXlsxImportService,
    tmp_path: Path,
) -> None:
    db.session.add(get_source())
    db.session.commit()

    import_file_path = write_xlsx(
        tmp_path / 'parking-sites.xlsx',
        [
            ['1', 'Parkhaus 1', 'Parkhaus', 48.1, 9.1, 100, 2, 4, 6, 8],
            ['2', 'Parkplatz 2', 'Parkplatz', 48.2, 9.2, 50, None, None, None, None],
        ],
    )

    parking_site_xlsx_import_service.load_and_import_parking_sites('source', import_file_path)

    parking_sites = db.session.query(ParkingSite).order_by(ParkingSite.original_uid).all()
    assert len(parking_sites) == 2
    assert get_restriction_capacities(parking_sites[0]) == {
        ParkingAudience.CARSHARING: 2,
        ParkingAudience.CHARGING: 4,
        ParkingAudience.WOMEN: 6,
        ParkingAudience.DISABLED: 8,
    }
    assert parking_sites[1].restrictions == []


def test_xlsx_import_replaces_capacity_restrictions(
    db: SQLAlchemy,
    parking_site_xlsx_import_service: ParkingSiteXlsxImportService,
    tmp_path: Path,
) -> None:
    parking_site = get_parking_site(
        source=get_source(),
        original_uid='1',
        restrictions=[
            get_parking_restriction(type=ParkingAudience.DISABLED, capacity=1),
            get_parking_restriction(type=ParkingAudience.CUSTOMER),
        ],
    )
    db.session.add(parking_site)
    db.session.commit()

    import_file_path = write_xlsx(
        tmp_path / 'parking-sites.xlsx',
        [['1', 'Parkhaus 1', 'Parkhaus', 48.1, 9.1, 100, None, None, None, 8]],
    )

    parking_site_xlsx_import_service.load_and_import_parking_sites('source', import_file_path)

    db.session.refresh(parking_site)
    assert get_restriction_capacities(parking_site) == {
        ParkingAudience.CUSTOMER: None,
        ParkingAudience.DISABLED: 8,
    }
