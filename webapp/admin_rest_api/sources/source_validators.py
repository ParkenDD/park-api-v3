"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import BooleanValidator, StringValidator, UrlValidator


class InconsistentSourceError(ValidationError):
    code = 'inconsistent_source'


@validataclass
class SourceInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(max_length=256)
    has_realtime_data: bool = BooleanValidator()
    timezone: str = StringValidator(), Default('Europe/Berlin')
    public_url: str | None = UrlValidator()
    attribution_license: str | None = StringValidator()
    attribution_url: str | None = StringValidator()
    attribution_contributor: str | None = StringValidator()

    def __post_validate__(self, *, source_uid: str, **kwargs):
        if self.uid != source_uid:
            raise InconsistentSourceError(reason='uid cannot be the same as the source uid')
