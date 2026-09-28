"""remove legacy capacities

Revision ID: 3f8a2d6c1e94
Revises: 7c2e1f4a9b3d
Create Date: 2026-09-27 12:00:00.000000

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3f8a2d6c1e94'
down_revision = '7c2e1f4a9b3d'
branch_labels = None
depends_on = None

audiences: dict[str, str] = {
    'disabled': 'DISABLED',
    'woman': 'WOMEN',
    'family': 'FAMILY',
    'charging': 'CHARGING',
    'carsharing': 'CARSHARING',
    'truck': 'TRUCK',
    'bus': 'BUS',
}

legacy_columns: list[str] = [
    f'{prefix}capacity_{audience}' for prefix in ['', 'realtime_', 'realtime_free_'] for audience in audiences
]


def upgrade():
    connection = op.get_bind()

    parking_site_table = sa.table(
        'parking_site',
        sa.column('id', sa.BigInteger()),
        *[sa.column(legacy_column, sa.Integer()) for legacy_column in legacy_columns],
    )
    parking_restriction_table = sa.table(
        'parking_restriction',
        sa.column('parking_site_id', sa.BigInteger()),
        sa.column('type', sa.String()),
        sa.column('capacity', sa.Integer()),
        sa.column('realtime_capacity', sa.Integer()),
        sa.column('realtime_free_capacity', sa.Integer()),
        sa.column('created_at', sa.DateTime()),
        sa.column('modified_at', sa.DateTime()),
    )

    # Move legacy capacities to restrictions if there is no restriction for this audience yet
    now = datetime.now(tz=timezone.utc)
    for audience_key, audience in audiences.items():
        rows = connection.execute(
            sa.select(
                parking_site_table.c.id,
                parking_site_table.c[f'capacity_{audience_key}'],
                parking_site_table.c[f'realtime_capacity_{audience_key}'],
                parking_site_table.c[f'realtime_free_capacity_{audience_key}'],
            ).where(
                parking_site_table.c[f'capacity_{audience_key}'].is_not(None),
                ~sa.exists().where(
                    parking_restriction_table.c.parking_site_id == parking_site_table.c.id,
                    parking_restriction_table.c.type == audience,
                ),
            ),
        ).all()

        if not rows:
            continue

        op.bulk_insert(
            parking_restriction_table,
            [
                {
                    'parking_site_id': row[0],
                    'type': audience,
                    'capacity': row[1],
                    'realtime_capacity': row[2],
                    'realtime_free_capacity': row[3],
                    'created_at': now,
                    'modified_at': now,
                }
                for row in rows
            ],
        )

    for table_name in ['parking_site', 'parking_site_history']:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            for legacy_column in legacy_columns:
                batch_op.drop_column(legacy_column)


def downgrade():
    # Legacy capacities are not restored, they are available as restrictions
    for table_name in ['parking_site', 'parking_site_history']:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            for legacy_column in legacy_columns:
                batch_op.add_column(sa.Column(legacy_column, sa.Integer(), nullable=True))
