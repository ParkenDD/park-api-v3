"""parking spot orientation

Revision ID: a4d9e3b7c215
Revises: 3f8a2d6c1e94
Create Date: 2026-10-20 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a4d9e3b7c215'
down_revision = '3f8a2d6c1e94'
branch_labels = None
depends_on = None

orientation: list[str] = ['PARALLEL', 'DIAGONAL', 'PERPENDICULAR']


def upgrade():
    # ParkingSiteOrientation got renamed to ParkingOrientation, so the Postgresql enum type has to follow
    engine_name = op.get_bind().engine.name
    if engine_name == 'postgresql':
        op.execute('ALTER TYPE parkingsiteorientation RENAME TO parkingorientation')

    with op.batch_alter_table('parking_spot', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'orientation',
                sa.Enum(*orientation, name='parkingorientation'),
                nullable=True,
            )
        )


def downgrade():
    with op.batch_alter_table('parking_spot', schema=None) as batch_op:
        batch_op.drop_column('orientation')

    engine_name = op.get_bind().engine.name
    if engine_name == 'postgresql':
        op.execute('ALTER TYPE parkingorientation RENAME TO parkingsiteorientation')
