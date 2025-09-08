"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timedelta, timezone

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper
from webapp.common.logging import Logger
from webapp.models.source import SourceStatus
from webapp.prometheus_api.prometheus_models import Metrics, MetricType, ParkingSiteMetric, SourceMetric
from webapp.repositories import ParkingSiteRepository, ParkingSpotRepository, SourceRepository


class PrometheusHandler:
    logger: Logger
    config_helper: ConfigHelper
    event_helper: EventHelper
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository
    parking_spot_repository: ParkingSpotRepository

    def __init__(
        self,
        logger: Logger,
        config_helper: ConfigHelper,
        event_helper: EventHelper,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
        parking_spot_repository: ParkingSpotRepository,
    ):
        self.logger = logger
        self.config_helper = config_helper
        self.event_helper = event_helper
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository
        self.parking_spot_repository = parking_spot_repository

    def get_metrics(self) -> str:
        sources = self.source_repository.fetch_sources()

        older_then_delta = timedelta(minutes=self.config_helper.get('REALTIME_OUTDATED_AFTER_MINUTES'))
        older_then = datetime.now(tz=timezone.utc) - older_then_delta

        parking_site_count_by_source = self.parking_site_repository.count_by_source()
        parking_spot_count_by_source = self.parking_spot_repository.count_by_source()

        realtime_outdated_parking_sites_by_source = (
            self.parking_site_repository.fetch_realtime_outdated_parking_site_count_by_source(older_then)
        )

        realtime_outdated_parking_spots_by_source = (
            self.parking_spot_repository.fetch_realtime_outdated_parking_spot_count_by_source(older_then)
        )

        last_static_update_metrics = Metrics(
            help='Last static update in seconds from now',
            type=MetricType.gauge,
            identifier='app_park_api_source_last_static_update',
        )
        last_realtime_update_metrics = Metrics(
            help='Last realtime update in seconds from now',
            type=MetricType.gauge,
            identifier='app_park_api_source_last_realtime_update',
        )
        source_parking_site_count = Metrics(
            help='Parking site count by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_site_count',
        )
        source_parking_spot_count = Metrics(
            help='Parking spot count by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_spot_count',
        )
        source_static_parking_site_errors = Metrics(
            help='Parking site static errors by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_site_static_errors',
        )
        legacy_source_static_parking_site_errors = Metrics(
            help='Parking site static errors by source',
            type=MetricType.gauge,
            identifier='app_static_park_api_source_errors',
        )
        source_realtime_parking_site_errors = Metrics(
            help='Parking site realtime error by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_site_realtime_errors',
        )
        legacy_source_realtime_parking_site_errors = Metrics(
            help='Parking site realtime error by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_errors',
        )
        source_static_parking_spot_errors = Metrics(
            help='Parking site static errors by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_spot_static_errors',
        )
        source_realtime_parking_spot_errors = Metrics(
            help='Parking site realtime error by source',
            type=MetricType.gauge,
            identifier='app_park_api_source_parking_spot_realtime_errors',
        )
        failed_static_sources = Metrics(
            help='Completely failed static sources',
            type=MetricType.gauge,
            identifier='app_park_api_static_source_failed',
        )
        failed_realtime_sources = Metrics(
            help='Completely failed realtime sources',
            type=MetricType.gauge,
            identifier='app_park_api_realtime_source_failed',
        )
        outdated_realtime_parking_sites = Metrics(
            help='Outdated realtime parking sites',
            type=MetricType.gauge,
            identifier='app_park_api_outdated_realtime_parking_sites',
        )
        outdated_realtime_parking_spots = Metrics(
            help='Outdated realtime parking spots',
            type=MetricType.gauge,
            identifier='app_park_api_outdated_realtime_parking_spots',
        )

        for source in sources:
            if source.static_status in [SourceStatus.DISABLED, SourceStatus.PROVISIONED]:
                continue

            if source.id in parking_site_count_by_source:
                source_parking_site_count.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=parking_site_count_by_source[source.id],
                    ),
                )

            if source.id in parking_spot_count_by_source:
                source_parking_spot_count.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=parking_spot_count_by_source[source.id],
                    ),
                )

            if source.static_data_updated_at:
                last_static_update_metrics.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=int((datetime.now(tz=timezone.utc) - source.static_data_updated_at).total_seconds()),
                    )
                )
            if source.static_parking_site_error_count is not None:
                source_static_parking_site_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.static_parking_site_error_count,
                    )
                )
                legacy_source_static_parking_site_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.static_parking_site_error_count,
                    )
                )
            if source.static_parking_spot_error_count is not None:
                source_static_parking_spot_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.static_parking_spot_error_count,
                    )
                )
            failed_static_sources.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=1 if source.static_status == SourceStatus.FAILED else 0,
                )
            )

            if source.realtime_status in [SourceStatus.DISABLED, SourceStatus.PROVISIONED]:
                continue

            if source.realtime_data_updated_at:
                last_realtime_update_metrics.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=int((datetime.now(tz=timezone.utc) - source.realtime_data_updated_at).total_seconds()),
                    )
                )
            if source.realtime_parking_site_error_count is not None:
                source_realtime_parking_site_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.realtime_parking_site_error_count,
                    )
                )
                legacy_source_realtime_parking_site_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.realtime_parking_site_error_count,
                    )
                )
            if source.realtime_parking_spot_error_count is not None:
                source_realtime_parking_spot_errors.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=source.realtime_parking_spot_error_count,
                    )
                )
            failed_realtime_sources.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=1 if source.realtime_status == SourceStatus.FAILED else 0,
                )
            )
            outdated_realtime_parking_sites.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=realtime_outdated_parking_sites_by_source.get(source.id, 0),
                ),
            )
            outdated_realtime_parking_spots.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=realtime_outdated_parking_spots_by_source.get(source.id, 0),
                ),
            )

        metrics = (
            source_parking_site_count.to_metrics()
            + source_parking_spot_count.to_metrics()
            + failed_static_sources.to_metrics()
            + last_static_update_metrics.to_metrics()
            + source_static_parking_site_errors.to_metrics()
            + legacy_source_static_parking_site_errors.to_metrics()
            + source_static_parking_spot_errors.to_metrics()
            + failed_realtime_sources.to_metrics()
            + last_realtime_update_metrics.to_metrics()
            + source_realtime_parking_site_errors.to_metrics()
            + legacy_source_realtime_parking_site_errors.to_metrics()
            + source_realtime_parking_spot_errors.to_metrics()
            + outdated_realtime_parking_sites.to_metrics()
            + outdated_realtime_parking_spots.to_metrics()
        )

        if self.config_helper.get('PARKING_SITE_METRICS', False):
            metrics += self.get_parking_site_metrics()

        return '\n'.join(metrics)

    def get_parking_site_metrics(self) -> list[str]:
        parking_sites = self.parking_site_repository.fetch_parking_sites(include_source=True)

        parking_site_static_capacity = Metrics(
            help='Parking site static capacity',
            type=MetricType.gauge,
            identifier='app_park_api_parking_site_static_capacity',
        )
        parking_site_realtime_capacity = Metrics(
            help='Parking site realtime capacity',
            type=MetricType.gauge,
            identifier='app_park_api_parking_site_realtime_capacity',
        )
        parking_site_realtime_free_capacity = Metrics(
            help='Parking site realtime free capacity',
            type=MetricType.gauge,
            identifier='app_park_api_parking_site_realtime_free_capacity',
        )

        for parking_site in parking_sites:
            if parking_site.capacity is None:
                continue
            parking_site_static_capacity.metrics.append(
                ParkingSiteMetric(
                    parking_site_uid=parking_site.original_uid,
                    source=parking_site.source.uid,
                    value=parking_site.capacity,
                    parking_site_name=parking_site.name,
                )
            )
            if not parking_site.has_realtime_data:
                continue

            if parking_site.realtime_capacity is None:
                continue
            parking_site_realtime_capacity.metrics.append(
                ParkingSiteMetric(
                    parking_site_uid=parking_site.original_uid,
                    source=parking_site.source.uid,
                    value=parking_site.realtime_capacity,
                    parking_site_name=parking_site.name,
                )
            )
            if parking_site.realtime_free_capacity is None:
                continue
            parking_site_realtime_free_capacity.metrics.append(
                ParkingSiteMetric(
                    parking_site_uid=parking_site.original_uid,
                    source=parking_site.source.uid,
                    value=parking_site.realtime_free_capacity,
                    parking_site_name=parking_site.name,
                )
            )

        return (
            parking_site_static_capacity.to_metrics()
            + parking_site_realtime_capacity.to_metrics()
            + parking_site_realtime_free_capacity.to_metrics()
        )
