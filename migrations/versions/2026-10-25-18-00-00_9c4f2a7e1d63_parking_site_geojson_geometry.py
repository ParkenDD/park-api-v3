"""parking site geojson geometry

Revision ID: 9c4f2a7e1d63
Revises: 5b1e7c9d2f48
Create Date: 2026-10-25 18:00:00.000000

"""

import json

import sqlalchemy as sa
from alembic import op
from shapely.errors import GEOSException
from shapely.geometry import shape

from webapp.common.sqlalchemy.geometry import Geometry

# revision identifiers, used by Alembic.
revision = '9c4f2a7e1d63'
down_revision = '5b1e7c9d2f48'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.add_column(sa.Column('geojson_geometry', Geometry(), nullable=True))

    connection = op.get_bind()
    engine_name = connection.engine.name

    # MySQL spatial indexes require NOT NULL columns, so just PostgreSQL gets an index
    if engine_name == 'postgresql':
        op.execute('CREATE INDEX ix_parking_site_geojson_geometry ON parking_site USING GIST (geojson_geometry);')
        update_statement = sa.text(
            'UPDATE parking_site SET geojson_geometry = ST_GeomFromText(:wkt, 4326) WHERE id = :id'
        )
    elif engine_name == 'mysql':
        update_statement = sa.text(
            "UPDATE parking_site SET geojson_geometry = ST_GeomFromText(:wkt, 4326, 'axis-order=long-lat') "
            'WHERE id = :id'
        )
    else:
        raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')

    # Backfill existing geojson. Parsing happens in Python, so broken geojson is skipped instead of failing.
    rows = connection.execute(sa.text('SELECT id, geojson FROM parking_site WHERE geojson IS NOT NULL')).fetchall()
    updates: list[dict] = []
    for row in rows:
        try:
            geometry = shape(json.loads(row.geojson))
        except (AttributeError, KeyError, TypeError, ValueError, GEOSException):
            continue
        if geometry.is_empty:
            continue
        updates.append({'id': row.id, 'wkt': geometry.wkt})

    if updates:
        connection.execute(update_statement, updates)


def downgrade():
    connection = op.get_bind()
    if connection.engine.name == 'postgresql':
        op.execute('DROP INDEX ix_parking_site_geojson_geometry;')

    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.drop_column('geojson_geometry')
