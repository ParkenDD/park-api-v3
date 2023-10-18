"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from sqlalchemy.sql.type_api import UserDefinedType

from webapp.extensions import db


class Point(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kwargs) -> str:
        engine_name = db.session.get_bind().dialect.name
        if engine_name == 'postgresql':
            return 'GEOMETRY'

        if engine_name == 'mysql':
            return 'POINT'

        raise NotImplementedError('The application just supports mysql, mariadb and postgresql.')
