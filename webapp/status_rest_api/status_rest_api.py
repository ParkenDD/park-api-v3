"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from parkapi_sources.version import __version__ as parkapi_sources_version

from webapp.common.blueprint import Blueprint
from webapp.common.rest import BaseMethodView


class StatusRestApi(Blueprint):
    def __init__(self):
        super().__init__('status', __name__, url_prefix='/')

        self.add_url_rule(
            '',
            view_func=RootStatusMethodView.as_view(
                'root-status',
                **self.get_base_method_view_dependencies(),
            ),
        )


class RootStatusMethodView(BaseMethodView):
    def get(self):
        return jsonify({
            'application': 'park-api-v3',
            'version': self.config_helper.get('PROJECT_VERSION'),
            'parkapi_sources_version': parkapi_sources_version,
            'documentation': {
                'public': f'{self.config_helper.get("PROJECT_URL")}/documentation/public.html',
                'admin': f'{self.config_helper.get("PROJECT_URL")}/documentation/admin.html',
            },
        })
