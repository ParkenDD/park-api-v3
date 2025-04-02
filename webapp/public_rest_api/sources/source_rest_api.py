"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import jsonify
from flask_openapi.decorator import (
    ExampleListReference,
    Response,
    ResponseData,
    Schema,
    SchemaListReference,
    document,
)
from validataclass.validators import DataclassValidator

from webapp.dependencies import dependencies
from webapp.models import Source
from webapp.public_rest_api.base_blueprint import PublicApiBaseBlueprint
from webapp.public_rest_api.base_method_view import PublicApiBaseMethodView
from webapp.public_rest_api.sources.source_handler import SourceHandler
from webapp.public_rest_api.sources.source_validators import SourceSearchQueryInput
from webapp.shared.sources.source_schema import source_example, source_schema


class SourceBlueprint(PublicApiBaseBlueprint):
    documented: bool = True
    source_handler: SourceHandler

    def __init__(self):
        super().__init__('sources', __name__, url_prefix='/v3/sources')

        self.source_handler = SourceHandler(
            **self.get_base_handler_dependencies(),
            source_repository=dependencies.get_source_repository(),
        )

        self.add_url_rule(
            '',
            view_func=SourceListMethodView.as_view(
                'sources',
                **self.get_base_method_view_dependencies(),
                source_handler=self.source_handler,
            ),
        )

        self.add_url_rule(
            '/<int:source_id>',
            view_func=SourceItemMethodView.as_view(
                'source-by-id',
                **self.get_base_method_view_dependencies(),
                source_handler=self.source_handler,
            ),
        )


class SourceBaseMethodView(PublicApiBaseMethodView):
    source_handler: SourceHandler

    def __init__(self, *, source_handler: SourceHandler, **kwargs):
        super().__init__(**kwargs)
        self.source_handler = source_handler


class SourceListMethodView(SourceBaseMethodView):
    source_search_query_validator = DataclassValidator(SourceSearchQueryInput)

    @document(
        description='Get Sources.',
        response=[
            Response(
                ResponseData(
                    schema=SchemaListReference('Source'),
                    example=ExampleListReference('Source'),
                )
            )
        ],
        components=[Schema('Source', schema=source_schema, example=source_example)],
    )
    def get(self):
        search_query = self.validate_query_args(self.source_search_query_validator)

        sources = self.source_handler.get_source_list(search_query=search_query)

        sources = sources.map(Source.to_dict)

        return self.jsonify_paginated_response(sources, search_query)


class SourceItemMethodView(SourceBaseMethodView):
    def get(self, source_id: int):
        source = self.source_handler.get_source_item(source_id)

        return jsonify(source.to_dict())
