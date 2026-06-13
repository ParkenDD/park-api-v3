"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import scoped_session

from webapp.repositories.exceptions import ObjectNotFoundException


class OfficialRegionCodeRepository:
    """
    A rather special repository for official regional codes (German Regionalschlüssel / Gemeindeschlüssel), which are
    not managed by our ORM. The `regionalschluessel` table is imported separately via ogr2ogr (see
    scripts/import-regionalschluessel.sh).
    """

    session: scoped_session

    def __init__(self, *, session: scoped_session) -> None:
        self.session = session

    def available_databases_by_country(self) -> list[str]:
        # So far, we just support the German Regionalschlüssel, which is imported into PostGIS via ogr2ogr. The lookup
        # relies on PostGIS spatial functions, so it is not available on MySQL/MariaDB.
        if self.session.get_bind().dialect.name != 'postgresql':
            return []

        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'regionalschluessel'"
        result = list(self.session.execute(text(query)))
        return ['DEU'] if len(result) else []

    def fetch_official_region_code_by_coordinates(self, country: str, lat: Decimal, lon: Decimal) -> str:
        if country != 'DEU':
            raise ObjectNotFoundException('So far, only Germany is supported for regional keys')

        query = (
            f'SELECT regioschlüsselaufgefüllt '  # noqa: S608
            f'FROM regionalschluessel '
            # We can be sure that this is not an SQLi because we convert to float
            f'WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint({float(lon)}, {float(lat)}), 4326))'
        )
        result = list(self.session.execute(text(query)))

        if len(result) == 0:
            raise ObjectNotFoundException('no official regional code found for coordinates')

        return result[0][0]
