"""source converter type

Revision ID: 7e2b5d8a4c19
Revises: 9c4f2a7e1d63
Create Date: 2026-10-26 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from webapp.dependencies import dependencies

# revision identifiers, used by Alembic.
revision = '7e2b5d8a4c19'
down_revision = '9c4f2a7e1d63'
branch_labels = None
depends_on = None

converter_type_enum = sa.Enum('PULL', 'PUSH', name='sourceconvertertype')


def upgrade():
    connection = op.get_bind()
    converter_type_enum.create(connection, checkfirst=True)

    with op.batch_alter_table('source', schema=None) as batch_op:
        batch_op.add_column(sa.Column('converter_type', converter_type_enum, nullable=True))

    # Everything which is not a registered pull converter (eg generic sources) is a push converter
    connection.execute(sa.text("UPDATE source SET converter_type = 'PUSH'"))

    generic_import_service = dependencies.get_generic_import_service()
    pull_source_uids: list[str] = [
        source_uid
        for source_uid in generic_import_service.park_api_sources.converter_by_uid.keys()
        if generic_import_service.is_pull_source(source_uid)
    ]
    if pull_source_uids:
        connection.execute(
            sa.text("UPDATE source SET converter_type = 'PULL' WHERE uid IN :uids").bindparams(
                sa.bindparam('uids', expanding=True),
            ),
            {'uids': pull_source_uids},
        )

    with op.batch_alter_table('source', schema=None) as batch_op:
        batch_op.alter_column('converter_type', existing_type=converter_type_enum, nullable=False)


def downgrade():
    with op.batch_alter_table('source', schema=None) as batch_op:
        batch_op.drop_column('converter_type')

    converter_type_enum.drop(op.get_bind(), checkfirst=True)
