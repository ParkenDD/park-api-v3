"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.rest.exceptions import UnauthorizedException


class ServerApiUnauthorizedException(UnauthorizedException):
    code = 'unauthorized'
    http_status = 401


class ServerApiMissingRoleException(ServerApiUnauthorizedException):
    pass
