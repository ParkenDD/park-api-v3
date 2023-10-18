"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError

from webapp.common.error_handling.exceptions import AppException
from webapp.repositories.exceptions import ObjectNotFoundException


class ImportException(AppException):
    pass


class ImportDatasetException(AppException):
    code = 'dataset_import_error'
    dataset: dict
    exception: ValidationError | ObjectNotFoundException

    def __init__(self, *args, dataset: dict, exception: ValidationError | ObjectNotFoundException, **kwargs):
        super().__init__(message='dataset_validation_error')
        self.dataset = dataset
        self.exception = exception


class ConverterMissingException(AppException):
    code = 'converter_missing'
