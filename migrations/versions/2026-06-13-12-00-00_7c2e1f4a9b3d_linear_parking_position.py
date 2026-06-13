"""linear parking position

Revision ID: 7c2e1f4a9b3d
Revises: 79f193ac7f86
Create Date: 2026-06-13 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7c2e1f4a9b3d'
down_revision = '79f193ac7f86'
branch_labels = None
depends_on = None

linear_parking_position: list[str] = ['ROAD_CENTER_LINE', 'PARKING_CENTER_LINE']


def upgrade():
    sa.Enum(*linear_parking_position, name='linearparkingposition').create(op.get_bind())

    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'linear_parking_position',
                sa.Enum(*linear_parking_position, name='linearparkingposition'),
                nullable=True,
            )
        )


def downgrade():
    with op.batch_alter_table('parking_site', schema=None) as batch_op:
        batch_op.drop_column('linear_parking_position')

    sa.Enum(*linear_parking_position, name='linearparkingposition').drop(op.get_bind())
