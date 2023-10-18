"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.common.rest import BaseMethodView


class PublicApiBaseMethodView(BaseMethodView):
    """
    Base class derived from Flask MethodView for server REST API views.
    """

    documentation: list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.documentation = []
