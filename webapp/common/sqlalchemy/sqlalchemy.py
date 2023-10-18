"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy
from sqlalchemy import MetaData


class SQLAlchemy(BaseSQLAlchemy):
    """
    Custom app-specific extension of the `SQLAlchemy` class from Flask-SQLAlchemy.
    """

    # Naming convention for automatic naming of constraints
    _naming_convention = {
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_N_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_N_name)s',
        'pk': 'pk_%(table_name)s',
    }

    def __init__(self, *args, **kwargs):
        # Set custom query class and metadata
        kwargs.update(
            metadata=MetaData(naming_convention=self._naming_convention),
        )

        # Initialize Flask SQLAlchemy
        super().__init__(*args, **kwargs)
