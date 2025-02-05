"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import Default
from validataclass.validators import IntegerValidator, ListValidator, Noneable, StringValidator
from validataclass_search_queries.search_queries import search_query_dataclass


@search_query_dataclass
class GetDuplicatesInput:
    old_duplicates: list[list[int]] = (
        ListValidator(
            ListValidator(IntegerValidator(min_value=1), min_length=2, max_length=2),
        ),
        Default([]),
    )
    radius: int | None = Noneable(IntegerValidator(min_value=1)), Default(None)
    source_ids: list[int] | None = ListValidator(IntegerValidator(min_value=1)), Default(None)
    source_uids: list[str] | None = ListValidator(StringValidator(min_length=1)), Default(None)
