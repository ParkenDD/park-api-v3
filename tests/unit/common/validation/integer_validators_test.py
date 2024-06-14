"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest
from validataclass.exceptions import ValidationError

from webapp.common.validation.integer_validators import GermanDurationIntegerValidator


class IntegerValidatorsTest:
    @staticmethod
    @pytest.mark.parametrize(
        'input_str, output_int',
        [
            ('3 Stunden', 60 * 60 * 3),
            ('10 Tage', 60 * 60 * 24 * 10),
            ('1 Woche', 60 * 60 * 24 * 7),
            ('10 Monate', 60 * 60 * 24 * 30 * 10),
        ],
    )
    def test_german_duration_integer_validate_success(input_str: str, output_int: int):
        validator = GermanDurationIntegerValidator()
        result = validator.validate(input_str)
        assert result == output_int

    @staticmethod
    def test_german_duration_integer_validate_failure():
        validator = GermanDurationIntegerValidator()

        with pytest.raises(ValidationError):
            validator.validate('banana')
