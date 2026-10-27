"""mirror cursor

Revision ID: 5b1e7c9d2f48
Revises: a4d9e3b7c215
Create Date: 2026-10-25 12:00:00.000000

"""

import sqlalchemy as sa
import sqlalchemy_utc
from alembic import op

# revision identifiers, used by Alembic.
revision = '5b1e7c9d2f48'
down_revision = 'a4d9e3b7c215'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('source', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mirror_parking_site_cursor', sqlalchemy_utc.UtcDateTime(), nullable=True))
        batch_op.add_column(sa.Column('mirror_parking_spot_cursor', sqlalchemy_utc.UtcDateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('source', schema=None) as batch_op:
        batch_op.drop_column('mirror_parking_spot_cursor')
        batch_op.drop_column('mirror_parking_site_cursor')
