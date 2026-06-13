"""official region code

Revision ID: 79f193ac7f86
Revises: b88bc9bb7b4d
Create Date: 2026-06-11 08:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '79f193ac7f86'
down_revision = 'b88bc9bb7b4d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.add_column(sa.Column('official_region_code', sa.String(length=36), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_parking_site_official_region_code'), ['official_region_code'], unique=False
        )

    with op.batch_alter_table('parking_spot', schema=None) as batch_op:
        batch_op.add_column(sa.Column('official_region_code', sa.String(length=36), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_parking_spot_official_region_code'), ['official_region_code'], unique=False
        )


def downgrade():
    with op.batch_alter_table('parking_spot', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_parking_spot_official_region_code'))
        batch_op.drop_column('official_region_code')

    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_parking_site_official_region_code'))
        batch_op.drop_column('official_region_code')
