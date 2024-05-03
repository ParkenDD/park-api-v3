"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import Parameter, Response, ResponseData, document
from flask_openapi.schema import StringField
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput

from .datex2_handler import Datex2Handler
from .datex2_schema import datex2_parking_sites_example, datex2_parking_sites_schema


class Datex2Blueprint(PublicApiBaseBlueprint):
    documented: bool = True
    datex2_handler: Datex2Handler

    def __init__(self):
        super().__init__('datex2', __name__, url_prefix='/datex2')

        self.datex2_handler = Datex2Handler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '/json',
            view_func=Datex2JSONMethodView.as_view(
                'parking-sites',
                **self.get_base_method_view_dependencies(),
                datex2_handler=self.datex2_handler,
            ),
        )


class Datex2BaseMethodView(PublicApiBaseMethodView):
    datex2_handler: Datex2Handler

    def __init__(self, *, datex2_handler: Datex2Handler, **kwargs):
        super().__init__(**kwargs)
        self.datex2_handler = datex2_handler


class Datex2JSONMethodView(Datex2BaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    @document(
        description='Get Datex2 Parking Sites as JSON.',
        query=[
            Parameter('source_uid', schema=StringField()),
        ],
        response=[Response(ResponseData(datex2_parking_sites_schema, datex2_parking_sites_example))],
    )
    def get(self):
        search_query = self.validate_query_args(self.parking_site_search_query_validator)

        datex2_publication = self.datex2_handler.get_parking_sites(search_query=search_query)

        return jsonify(datex2_publication.to_dict())
