"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import make_response

from webapp.common.blueprint import Blueprint
from webapp.common.rest import BaseMethodView
from webapp.dependencies import dependencies
from webapp.prometheus_api.prometheus_handler import PrometheusHandler


class PrometheusRestApi(Blueprint):
    documentation_base = True

    def __init__(self):
        super().__init__('prometheus', __name__, url_prefix='/metrics')

        prometheus_handler = PrometheusHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '',
            view_func=MetricsMethodView.as_view(
                'metrics',
                **self.get_base_method_view_dependencies(),
                prometheus_handler=prometheus_handler,
            ),
        )


class MetricsMethodView(BaseMethodView):
    prometheus_handler: PrometheusHandler

    def __init__(self, *, prometheus_handler: PrometheusHandler, **kwargs):
        super().__init__(**kwargs)
        self.prometheus_handler = prometheus_handler

    def get(self):
        response_string = self.prometheus_handler.get_metrics()
        response = make_response(response_string)
        response.mimetype = 'text/plain; version=0.0.4'
        return response
