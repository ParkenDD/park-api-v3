"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import IntegerValidator, ListValidator, Noneable


@validataclass
class GetDuplicatesInput:
    old_duplicates: list[list[int]] = ListValidator(
        ListValidator(IntegerValidator(min_value=1), min_length=2, max_length=2),
    )
    radius: Optional[int] = Noneable(IntegerValidator(min_value=1)), Default(None)
