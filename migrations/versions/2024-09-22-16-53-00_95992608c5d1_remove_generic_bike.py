"""remove-generic-bike

Revision ID: 95992608c5d1
Revises: 3e92c13d297e
Create Date: 2024-09-22 16:53:00.630618

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '95992608c5d1'
down_revision = '3e92c13d297e'
branch_labels = None
depends_on = None

old_parking_site_types: list[str] = [
    'ON_STREET',
    'OFF_STREET_PARKING_GROUND',
    'UNDERGROUND',
    'CAR_PARK',
    'GENERIC_BIKE',
    'WALL_LOOPS',
    'SAFE_WALL_LOOPS',
    'STANDS',
    'LOCKERS',
    'SHED',
    'TWO_TIER',
    'BUILDING',
    'FLOOR',
    'LOCKBOX',
    'OTHER',
]

new_parking_site_types: list[str] = [
    'ON_STREET',
    'OFF_STREET_PARKING_GROUND',
    'UNDERGROUND',
    'CAR_PARK',
    'WALL_LOOPS',
    'SAFE_WALL_LOOPS',
    'STANDS',
    'LOCKERS',
    'SHED',
    'TWO_TIER',
    'BUILDING',
    'FLOOR',
    'LOCKBOX',
    'OTHER',
]


def upgrade():
    # Set all generic bike to other
    op.execute("UPDATE parking_site SET type = 'OTHER' WHERE type = 'GENERIC_BIKE'")

    # Prepare enums for Postgresql
    engine_name = op.get_bind().engine.name
    if engine_name == 'postgresql':
        op.execute('ALTER TYPE parkingsitetype RENAME TO _parkingsitetype')
        sa.Enum(
            *new_parking_site_types,
            name='parkingsitetype',
        ).create(op.get_bind())
        op.execute('ALTER TABLE parking_site ALTER COLUMN type type parkingsitetype using type::text::parkingsitetype;')
        sa.Enum(*old_parking_site_types, name='_parkingsitetype').drop(op.get_bind())

    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.alter_column(
            'type',
            existing_type=sa.Enum(*old_parking_site_types, name='parkingsitetype'),
            type_=sa.Enum(*new_parking_site_types, name='parkingsitetype'),
            existing_nullable=True,
        )


def downgrade():
    op.execute('ALTER TYPE parkingsitetype RENAME TO _parkingsitetype')
    sa.Enum(*old_parking_site_types, name='parkingsitetype').create(op.get_bind())
    op.execute('ALTER TABLE parking_site ALTER COLUMN type type parkingsitetype using type::text::parkingsitetype;')
    sa.Enum(*new_parking_site_types, name='_parkingsitetype').drop(op.get_bind())

    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.alter_column(
            'type',
            existing_type=sa.Enum(*new_parking_site_types, name='parkingsitetype'),
            type_=sa.Enum(*old_parking_site_types, name='parkingsitetype'),
            existing_nullable=True,
        )
