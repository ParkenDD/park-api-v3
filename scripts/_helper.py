"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from pathlib import Path


def load_duplicates(duplicates_file_path: Path, ignore: bool = False) -> list[tuple[int, int]]:
    old_duplicates: list[tuple[int, int]] = []
    first = True
    with open(duplicates_file_path) as duplicates_file:
        rows = csv.reader(duplicates_file)
        for row in rows:
            if first:
                # We ignore the first line as this is our header
                first = False
                continue
            # For applying, we just want to get ignored datasets
            if ignore and row[2] != 'IGNORE':
                continue
            old_duplicates.append((int(row[0]), int(row[1])))
    return old_duplicates


def save_duplicates(duplicates_file_path: Path, items: list[dict], append: bool = False):
    mapping = [
        'id',
        'duplicate_id',
        'status',
        'source_id',
        'source_uid',
        'lat',
        'lon',
        'name',
        'address',
        'capacity',
        'api_url',
        'type',
        'park_and_ride_type',
        'description',
        'photo_url',
        'public_url',
        'opening_hours',
    ]
    with open(duplicates_file_path, 'a' if append else 'w') as duplicates_file:
        duplicate_csv = csv.writer(duplicates_file)
        # Write header if not appending
        if append is False:
            duplicate_csv.writerow(mapping)
        for item in items:
            row = []
            for field in mapping:
                if item.get(field) is None:
                    value = ''
                elif isinstance(item[field], list):
                    value = ','.join(item[field])
                else:
                    value = str(item[field])
                row.append(value)
            duplicate_csv.writerow(row)
