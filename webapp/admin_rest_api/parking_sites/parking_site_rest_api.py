"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.validators import DataclassValidator

from webapp.admin_rest_api import AdminApiBaseBlueprint, AdminApiBaseMethodView
from webapp.common.json import empty_json_response
from webapp.dependencies import dependencies
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput

from .parking_site_handler import ParkingSiteHandler
from .parking_site_validators import ApplyDuplicatesInput, GetDuplicatesInput


class ParkingSitesBlueprint(AdminApiBaseBlueprint):
    documented: bool = True
    parking_site_handler: ParkingSiteHandler

    def __init__(self):
        super().__init__('admin-parking-sites', __name__, url_prefix='/parking-sites')

        self.parking_site_handler = ParkingSiteHandler(
            **self.get_base_handler_dependencies(),
            parking_site_repository=dependencies.get_parking_site_repository(),
            matching_service=dependencies.get_matching_service(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '',
            view_func=ParkingSitesMethodView.as_view(
                'admin-parking-sites',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/<int:parking_site_id>',
            view_func=ParkingSiteMethodView.as_view(
                'admin-parking-site',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/duplicates/generate',
            view_func=ParkingSiteDuplicatesGenerateMethodView.as_view(
                'admin-parking-site-duplicates-generate',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )
        self.add_url_rule(
            '/duplicates/apply',
            view_func=ParkingSiteDuplicatesApplyMethodView.as_view(
                'admin-parking-site-duplicates-apply',
                **self.get_base_method_view_dependencies(),
                parking_site_handler=self.parking_site_handler,
            ),
        )


class ParkingSiteBaseMethodView(AdminApiBaseMethodView):
    parking_site_handler: ParkingSiteHandler

    def __init__(self, *, parking_site_handler: ParkingSiteHandler, **kwargs):
        super().__init__(**kwargs)
        self.parking_site_handler = parking_site_handler


class ParkingSitesMethodView(ParkingSiteBaseMethodView):
    parking_site_search_query_validator = DataclassValidator(ParkingSiteSearchInput)

    def get(self):
        search_query = self.validate_query_args(self.parking_site_search_query_validator)

        return self.parking_site_handler.get_parking_sites(search_query=search_query)


class ParkingSiteMethodView(ParkingSiteBaseMethodView):
    def get(self, parking_site_id: int):
        self.parking_site_handler.get_parking_site(parking_site_id)


class ParkingSiteDuplicatesGenerateMethodView(ParkingSiteBaseMethodView):
    duplicate_validator = DataclassValidator(GetDuplicatesInput)

    def post(self):
        duplicate_input: GetDuplicatesInput = self.duplicate_validator.validate(self.request_helper.get_parsed_json())

        return self.parking_site_handler.generate_duplicates(duplicate_input)


class ParkingSiteDuplicatesApplyMethodView(ParkingSiteBaseMethodView):
    apply_duplicate_validator = DataclassValidator(ApplyDuplicatesInput)

    def post(self):
        apply_duplicate_input: ApplyDuplicatesInput = self.validate_request(self.apply_duplicate_validator)

        self.parking_site_handler.apply_duplicates(apply_duplicate_input)

        return empty_json_response(), 204
