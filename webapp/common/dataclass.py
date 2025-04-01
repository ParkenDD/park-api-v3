"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import asdict, is_dataclass
from typing import Any

from validataclass.helpers import UnsetValue


def recursive_to_dict(data: Any):
    if is_dataclass(data):
        return {key: recursive_to_dict(value) for key, value in asdict(data).items()}
    if isinstance(data, list):
        return [recursive_to_dict(item) for item in data]
    return data


def filter_unset_value(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: filter_unset_value(value) for key, value in data.items() if value is not UnsetValue}
    if isinstance(data, list):
        return [filter_unset_value(item) for item in data if item is not UnsetValue]
    return data


def filter_unset_value_and_none(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            key: filter_unset_value_and_none(value)
            for key, value in data.items()
            if value is not UnsetValue and value is not None
        }

    if isinstance(data, list):
        return [filter_unset_value_and_none(item) for item in data if item is not UnsetValue and item is not None]

    return data


class DataclassMixin:
    def to_dict(self):
        return filter_unset_value(recursive_to_dict(self))
