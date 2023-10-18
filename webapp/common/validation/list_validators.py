"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.validators import ListValidator, T_ListItem


class CommaSeparatedListValidator(ListValidator):
    def validate(self, input_data: Any, **kwargs) -> list[T_ListItem]:
        self._ensure_type(input_data, str)

        return super().validate(input_data.split(','), **kwargs)
